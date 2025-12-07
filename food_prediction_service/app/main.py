import os
from dotenv import load_dotenv
import firebase_admin
from fastapi import FastAPI, UploadFile, Request, Header, HTTPException
from firebase_admin import credentials
from typing import List

from sqlite_database.db import init_db
from sqlite_database.logger import log_upload, log_request, fetch_interactions_for_user

from authentication import verify_firebase_token
from firebase_database.firebase_client import (
    save_prediction,
    get_all_predictions,
    get_prediction,
    update_prediction,
    delete_prediction
)
from security import APISecurity
from instrumentation import setup_otel
from publisher import RabbitMQPublisher
from model import ThermitrackModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()

# Firebase Initialization
firebase_key_path = os.getenv("FIREBASE_KEY_PATH", "firebase-key.json")
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(firebase_key_path)
    firebase_admin.initialize_app(cred)

# FastAPI App and Instrumentation
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
setup_otel(app)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Services
image_validator = APISecurity()
food_predictor = ThermitrackModel()
publisher = RabbitMQPublisher()
init_db()


@app.get("/interactions")
@limiter.limit("5/minute")
async def get_api_interactions(
    request: Request,
    authorization: str = Header(None)
) -> dict:
    """
    Retrieve all logged API interactions for the authenticated user.

    Returns:
        dict: {"interactions": List[dict]}
    """
    user = verify_firebase_token(authorization)
    uid = user["uid"]

    interactions = fetch_interactions_for_user(uid)

    return {"interactions": interactions}


@app.post("/predict")
@limiter.limit("5/minute")
async def predict_and_save(
    request: Request,
    files: List[UploadFile],
    authorization: str = Header(None)
) -> dict:
    """
    Predict food items from uploaded images and save results.

    Validates uploaded images, performs prediction using ThermitrackModel,
    saves the results to Firebase, logs activity, and publishes
    messages to RabbitMQ.

    Args:
        request (Request): FastAPI request object.
        files (List[UploadFile]): Uploaded image files.
        authorization (str): Firebase Bearer token header.

    Returns:
        dict: {"results": List[dict]} containing document ID, prediction data, and filename.

    Raises:
        HTTPException: If authorization fails.
    """
    user = verify_firebase_token(authorization)
    uid = user["uid"]
    log_request(uid, "/predict", "POST")

    results = []

    for file in files:
        # Validate and rename image
        image_validator.validate_image(file)
        new_filename = image_validator.rename_image(file)

        # Perform prediction
        prediction = food_predictor.predict_food(file.file)

        # Save prediction to database
        doc_id = save_prediction({
            "userId": uid,
            "filename": file.filename,
            "prediction": prediction["Food"],
            "confidence": prediction["Confidence Score"]
        })

        # Log upload
        log_upload(
            user_id=uid,
            filename=new_filename,
            confidence=prediction["Confidence Score"]
        )

        # Publish message
        publisher.publish({
            "doc_id": doc_id,
            "food_name": prediction["Food"],
        })

        results.append({
            "id": doc_id,
            "prediction": prediction,
            "filename": file.filename
        })

    return {"results": results}


@app.get("/predictions")
@limiter.limit("5/minute")
async def list_predictions(
    request: Request,
    authorization: str = Header(None)
) -> dict:
    """
    Retrieve all predictions for the authenticated user.

    Args:
        request (Request): FastAPI request object.
        authorization (str): Firebase Bearer token header.

    Returns:
        dict: {"predictions": List[dict]} of user-specific predictions.
    """
    user = verify_firebase_token(authorization)
    uid = user["uid"]

    all_predictions = get_all_predictions()
    user_predictions = [p for p in all_predictions if p.get("userId") == uid]

    return {"predictions": user_predictions}


@app.put("/predictions/{doc_id}")
@limiter.limit("5/minute")
async def edit_prediction(
    request: Request,
    doc_id: str,
    updated_data: dict,
    authorization: str = Header(None)
) -> dict:
    """
    Edit a specific prediction for the authenticated user.

    Args:
        request (Request): FastAPI request object.
        doc_id (str): Document ID of the prediction.
        updated_data (dict): Fields to update.
        authorization (str): Firebase Bearer token header.

    Returns:
        dict: {"status": "updated"} on success.

    Raises:
        HTTPException: If prediction does not exist or user is unauthorized.
    """
    user = verify_firebase_token(authorization)
    uid = user["uid"]

    prediction = get_prediction(doc_id)
    if not prediction or prediction.get("userId") != uid:
        raise HTTPException(status_code=403, detail="Unauthorized")

    update_prediction(doc_id, updated_data)
    return {"status": "updated"}


@app.delete("/predictions/{doc_id}")
@limiter.limit("5/minute")
async def remove_prediction(
    request: Request,
    doc_id: str,
    authorization: str = Header(None)
) -> dict:
    """
    Delete a specific prediction for the authenticated user.

    Args:
        request (Request): FastAPI request object.
        doc_id (str): Document ID of the prediction.
        authorization (str): Firebase Bearer token header.

    Returns:
        dict: {"status": "deleted"} on success.

    Raises:
        HTTPException: If prediction does not exist or user is unauthorized.
    """
    user = verify_firebase_token(authorization)
    uid = user["uid"]

    prediction = get_prediction(doc_id)
    if not prediction or prediction.get("userId") != uid:
        raise HTTPException(status_code=403, detail="Unauthorized")

    delete_prediction(doc_id)
    return {"status": "deleted"}
