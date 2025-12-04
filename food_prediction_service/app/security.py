import os
import uuid
import logging
from fastapi import HTTPException, UploadFile

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class APISecurity:
    """
    API security utilities for validating and renaming uploaded images.

    Provides methods to:
    - Validate file size and type.
    - Rename uploaded files to unique identifiers.
    """

    # Configuration for validation
    config = {
        "MAXIMUM_FILE_SIZE": 50 * 1024 * 1024,  # 50 MB max
        "ALLOWED_MIME_TYPES": ["image/png", "image/jpg", "image/jpeg", "image/webp"],
        "ALLOWED_FILE_TYPES": [".jpg", ".jpeg", ".png", ".webp"],
    }

    def rename_image(self, file: UploadFile) -> str:
        """
        Generate a unique filename for an uploaded image.

        Args:
            file (UploadFile): The uploaded image file.

        Returns:
            str: A new filename with a unique UUID and original extension.
        """
        _, ext = os.path.splitext(file.filename)
        new_name = f"{uuid.uuid4().hex}{ext.lower()}"
        logger.debug(f"Renamed image '{file.filename}' to '{new_name}'")
        return new_name

    def validate_image_size(self, file: UploadFile) -> bool:
        """
        Validate that the uploaded image does not exceed the maximum allowed size.

        Args:
            file (UploadFile): The uploaded image file.

        Returns:
            bool: True if the file size is within the limit, False otherwise.
        """
        file.file.seek(0, 2)  # Seek to end of file
        size = file.file.tell()
        file.file.seek(0)  # Reset pointer to start
        logger.debug(f"Image size: {size} bytes")
        return size <= self.config["MAXIMUM_FILE_SIZE"]

    def validate_image_type(self, file: UploadFile) -> bool:
        """
        Validate the MIME type and file extension of the uploaded image.

        Args:
            file (UploadFile): The uploaded image file.

        Returns:
            bool: True if the file type is allowed, False otherwise.
        """
        if file.content_type not in self.config["ALLOWED_MIME_TYPES"]:
            logger.warning(f"Unsupported MIME type: {file.content_type}")
            return False

        _, ext = os.path.splitext(file.filename.lower())
        if ext not in self.config["ALLOWED_FILE_TYPES"]:
            logger.warning(f"Unsupported file extension: {ext}")
            return False

        return True

    def validate_image(self, file: UploadFile):
        """
        Perform all validations on the uploaded image and raise HTTP exceptions
        for invalid files.

        Args:
            file (UploadFile): The uploaded image file.

        Raises:
            HTTPException: 413 if file is too large.
            HTTPException: 415 if file type is unsupported.
        """
        if not self.validate_image_size(file):
            logger.error(f"Image too large: {file.filename}")
            raise HTTPException(
                status_code=413,
                detail="Payload Too Large.",
            )

        if not self.validate_image_type(file):
            logger.error(f"Unsupported image type: {file.filename}")
            raise HTTPException(
                status_code=415,
                detail="Unsupported Media Type.",
            )

