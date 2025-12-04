import logging
from typing import Optional

from firebase_admin import auth
from fastapi import HTTPException, Header, status

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def verify_firebase_token(authorization: Optional[str] = Header(None)) -> dict:
    """Verify a Firebase ID token from the Authorization header.

    Extracts the token from the `Authorization` header, validates its format,
    and verifies it using Firebase Admin SDK. Raises HTTPException if the
    token is missing, malformed, or invalid.

    Args:
        authorization (Optional[str]): The `Authorization` header in the format
            "Bearer <token>". Provided automatically if used as a FastAPI dependency.

    Returns:
        dict: Decoded Firebase token containing user info.

    Raises:
        HTTPException: If the header is missing, malformed, or the token is invalid/expired.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format",
        )

    token = authorization.split(" ", 1)[1]

    try:
        # Verify the token with Firebase
        decoded_token = auth.verify_id_token(token)
        return decoded_token

    except auth.ExpiredIdTokenError:
        logger.warning("Expired Firebase token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except auth.InvalidIdTokenError:
        logger.warning("Invalid Firebase token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"Error verifying Firebase token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not verify token",
        )


