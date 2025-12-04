from datetime import datetime
import sqlite3
from .db import get_connection


def log_upload(user_id: str, filename: str, confidence: float) -> None:
    """
    Log an image upload to the SQLite database.

    Inserts a record into the 'uploads' table, recording the user ID,
    filename, confidence score of the prediction, and the UTC timestamp
    of the upload.

    Args:
        user_id (str): The ID of the user performing the upload.
        filename (str): The name of the uploaded file.
        confidence (float): Confidence score of the prediction.

    Raises:
        sqlite3.Error: If the insert operation fails.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO uploads (user_id, filename, confidence, upload_time)
            VALUES (?, ?, ?, ?)
        """, (user_id, filename, confidence, datetime.utcnow().isoformat()))
        conn.commit()
    finally:
        conn.close()


def log_request(user_id: str, endpoint: str, method: str) -> None:
    """
    Log an API request to the SQLite database.

    Inserts a record into the 'api_requests' table, recording the user ID,
    endpoint accessed, HTTP method used, and the UTC timestamp of the request.

    Args:
        user_id (str): The ID of the user making the request.
        endpoint (str): The API endpoint accessed.
        method (str): HTTP method used (GET, POST, PUT, DELETE, etc.).

    Raises:
        sqlite3.Error: If the insert operation fails.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO api_requests (user_id, endpoint, method, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user_id, endpoint, method, datetime.utcnow().isoformat()))
        conn.commit()
    finally:
        conn.close()

