import logging
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("/app/sqlite_database/stats.db")

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


logger.info(f"SQLite DB will be created at: {DB_PATH}")


def get_connection() -> sqlite3.Connection:
    """
    Get a connection to the SQLite database.

    Ensures that the parent directory exists before connecting.

    Returns:
        sqlite3.Connection: Connection object to the database.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)  # Ensure folder exists
    return sqlite3.connect(DB_PATH)


def init_db():
    """
    Initialize the SQLite database.

    Creates tables for:
        - uploads: Tracks uploaded images (user, filename, confidence, timestamp)
        - api_requests: Tracks API requests (user, endpoint, method, timestamp)

    Tables are created only if they do not already exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Table for tracking uploaded images
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            filename TEXT NOT NULL,
            confidence REAL NOT NULL,
            upload_time TEXT NOT NULL
        )
    """)

    # Table for tracking API requests
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            method TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    conn.commit()  # Save changes
    conn.close()   # Close connection
