import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional, List, Dict, Union

# Initialize Firebase app
cred = credentials.Certificate("firebase_database/firebase_key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def save_prediction(prediction_data: Dict) -> str:
    """
    Save a new prediction document to Firestore.

    Args:
        prediction_data (dict): Dictionary containing prediction details,
            e.g., userId, filename, prediction, confidence.

    Returns:
        str: Firestore document ID of the newly created prediction.
    """
    doc_ref = db.collection("predictions").document()
    doc_ref.set(prediction_data)
    return doc_ref.id


def get_all_predictions(user_id: Optional[str] = None) -> List[Dict]:
    """
    Retrieve all predictions or only those belonging to a specific user.

    Args:
        user_id (Optional[str]): If provided, filters predictions for this user.

    Returns:
        List[dict]: List of prediction dictionaries, each including 'id' field.
    """
    predictions_ref = db.collection("predictions")
    if user_id:
        predictions_ref = predictions_ref.where("userId", "==", user_id)
    docs = predictions_ref.stream()
    return [{**doc.to_dict(), "id": doc.id} for doc in docs]


def get_prediction(doc_id: str) -> Optional[Dict]:
    """
    Retrieve a single prediction by document ID.

    Args:
        doc_id (str): Firestore document ID.

    Returns:
        dict or None: Prediction dictionary with 'id' field if found, else None.
    """
    doc = db.collection("predictions").document(doc_id).get()
    if doc.exists:
        return {**doc.to_dict(), "id": doc.id}
    return None


def update_prediction(doc_id: str, updated_data: Dict):
    """
    Update an existing prediction document with new data.

    Args:
        doc_id (str): Firestore document ID.
        updated_data (dict): Fields to update.

    Raises:
        firebase_admin.exceptions.FirebaseError: If update fails.
    """
    db.collection("predictions").document(doc_id).update(updated_data)


def delete_prediction(doc_id: str):
    """
    Delete a prediction document from Firestore.

    Args:
        doc_id (str): Firestore document ID.

    Raises:
        firebase_admin.exceptions.FirebaseError: If deletion fails.
    """
    db.collection("predictions").document(doc_id).delete()

