import pytest
from fastapi import HTTPException
from unittest.mock import patch

# ✅ CORRECT IMPORT
from food_prediction_service.app.authentication import verify_firebase_token


def test_missing_authorization():
    with pytest.raises(HTTPException) as exc_info:
        verify_firebase_token(None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Authorization header missing"


def test_invalid_header_format():
    with pytest.raises(HTTPException) as exc_info:
        verify_firebase_token("InvalidHeader")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid Authorization header format"


# ✅ CORRECT PATCH PATH
@patch("food_prediction_service.app.authentication.auth.verify_id_token")
def test_valid_token(mock_verify):
    mock_verify.return_value = {"uid": "12345", "email": "test@example.com"}

    result = verify_firebase_token("Bearer valid_token")

    assert result == {"uid": "12345", "email": "test@example.com"}
    mock_verify.assert_called_once_with("valid_token")


@patch("food_prediction_service.app.authentication.auth.verify_id_token")
def test_expired_token(mock_verify):
    from firebase_admin import auth as firebase_auth
    mock_verify.side_effect = firebase_auth.ExpiredIdTokenError("Token expired", "expired")

    with pytest.raises(HTTPException) as exc_info:
        verify_firebase_token("Bearer expired_token")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has expired"


@patch("food_prediction_service.app.authentication.auth.verify_id_token")
def test_invalid_token(mock_verify):
    from firebase_admin import auth as firebase_auth
    mock_verify.side_effect = firebase_auth.InvalidIdTokenError("Invalid token")

    with pytest.raises(HTTPException) as exc_info:
        verify_firebase_token("Bearer invalid_token")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


@patch("food_prediction_service.app.authentication.auth.verify_id_token")
def test_unexpected_error(mock_verify):
    mock_verify.side_effect = Exception("Some error")

    with pytest.raises(HTTPException) as exc_info:
        verify_firebase_token("Bearer some_token")

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not verify token"

