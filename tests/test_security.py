import io
import pytest
from fastapi import UploadFile, HTTPException
from food_prediction_service.app.security import APISecurity

class FileUpload(UploadFile):
    """FileUpload subclass that allows setting content_type for tests."""
    def __init__(self, filename, content_bytes, content_type):
        super().__init__(filename=filename, file=io.BytesIO(content_bytes))
        self._content_type = content_type

    @property
    def content_type(self):
        return self._content_type


def create_upload_file(filename, content_type, content_bytes):
    return FileUpload(filename, content_bytes, content_type)


def test_rename_image_generates_unique_name():
    security = APISecurity()
    file = create_upload_file("test.jpg", "image/jpeg", b"fakecontent")

    new_name = security.rename_image(file)
    assert new_name.endswith(".jpg")
    assert new_name != file.filename
    assert len(new_name) > len(".jpg")


def test_validate_image_size_under_limit():
    security = APISecurity()
    small_file = create_upload_file("small.jpg", "image/jpeg", b"x" * 1024)
    assert security.validate_image_size(small_file) is True


def test_validate_image_size_over_limit():
    security = APISecurity()
    large_file = create_upload_file("large.jpg", "image/jpeg", b"x" * (APISecurity.config["MAXIMUM_FILE_SIZE"] + 1))
    assert security.validate_image_size(large_file) is False


def test_validate_image_type_valid():
    security = APISecurity()
    file = create_upload_file("valid.webp", "image/webp", b"x" * 1024)
    assert security.validate_image_type(file) is True


def test_validate_image_type_invalid_mime():
    security = APISecurity()
    file = create_upload_file("image.jpg", "application/pdf", b"x" * 1024)
    assert security.validate_image_type(file) is False


def test_validate_image_type_invalid_extension():
    security = APISecurity()
    file = create_upload_file("image.txt", "image/jpeg", b"x" * 1024)
    assert security.validate_image_type(file) is False


def test_validate_image_raises_http_exception_on_size():
    security = APISecurity()
    file = create_upload_file("large.jpg", "image/jpeg", b"x" * (APISecurity.config["MAXIMUM_FILE_SIZE"] + 1))

    with pytest.raises(HTTPException) as exc:
        security.validate_image(file)
    assert exc.value.status_code == 413


def test_validate_image_raises_http_exception_on_type():
    security = APISecurity()
    file = create_upload_file("image.txt", "image/jpeg", b"x" * 1024)

    with pytest.raises(HTTPException) as exc:
        security.validate_image(file)
    assert exc.value.status_code == 415