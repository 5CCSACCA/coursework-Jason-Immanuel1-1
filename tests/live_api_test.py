import logging
import time

import requests
import os
from dotenv import load_dotenv


load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class LiveAPITestClient:
    def __init__(self):
        self.firebase_api_key = os.getenv("FIREBASE_API_KEY")
        self.email = os.getenv("EMAIL")
        self.password = os.getenv("PASSWORD")
        self.api_base_url = os.getenv("API_BASE_URL")
        self.token = None

    def login(self):
        """Authenticate with Firebase and store JWT token."""
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.firebase_api_key}"
        data = {
            "email": self.email,
            "password": self.password,
            "returnSecureToken": True
        }

        response = requests.post(url, json=data)
        response.raise_for_status()

        self.token = response.json()["idToken"]
        logger.info("Login successful")

    def predict(self, image_path: str):
        """Send real image to /predict endpoint."""
        if not self.token:
            raise RuntimeError("You must login before predicting.")

        url = f"{self.api_base_url}/predict"
        headers = {"Authorization": f"Bearer {self.token}"}

        with open(image_path, "rb") as f:
            files = [
                ("files", (os.path.basename(image_path), f, "image/jpeg"))
            ]

            response = requests.post(url, headers=headers, files=files, verify=False)
            response.raise_for_status()

            logger.info("Prediction successful")
            return response.json()

    def list_predictions(self):
        """Fetch all predictions for logged-in user."""
        url = f"{self.api_base_url}/predictions"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()

        logger.info("Fetched predictions")
        return response.json()

    def list_interactions(self):
        """Fetch all API interactions for logged-in user."""
        url = f"{self.api_base_url}/interactions"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()

        logger.info("Fetched API interactions")
        return response.json()
        return response.json()

    def update_prediction(self, doc_id: str, new_data: dict):
        """Update an existing prediction."""
        url = f"{self.api_base_url}/predictions/{doc_id}"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.put(url, headers=headers, json=new_data, verify=False)
        response.raise_for_status()

        logger.info("Prediction updated")
        return response.json()

    def delete_prediction(self, doc_id: str):
        """Delete an existing prediction."""
        url = f"{self.api_base_url}/predictions/{doc_id}"
        headers = {"Authorization": f"Bearer {self.token}"}

        response = requests.delete(url, headers=headers, verify=False)
        response.raise_for_status()

        logger.info("Prediction deleted")
        return response.json()

if __name__ == "__main__":
    client = LiveAPITestClient()

    # LOGIN
    client.login()
    time.sleep(5)

    # PREDICT
    image_path = "test_images/pizza.jpg"
    predict_response = client.predict(image_path)
    logger.info(f"Predict response: {predict_response}")
    time.sleep(5)

    doc_id = predict_response["results"][0]["id"]

    # GET USER PREDICTIONS
    predictions = client.list_predictions()
    logger.info(f"User predictions: {predictions}")
    time.sleep(5)

    # GET USER API INTERACTIONS
    interactions = client.list_interactions()
    logger.info(f"User interactions: {interactions}")
    time.sleep(5)

    # UPDATE PREDICTION
    update_response = client.update_prediction(
        doc_id,
        {"prediction": "Updated Food Name"}
    )
    logger.info(f"Update response: {update_response}")
    time.sleep(5)

    # DELETE PREDICTION
    delete_response = client.delete_prediction(doc_id)
    logger.info(f"Delete response: {delete_response}")
