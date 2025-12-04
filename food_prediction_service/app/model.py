from ultralytics import YOLO
from PIL import Image, UnidentifiedImageError
from typing import Union, BinaryIO
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ThermitrackModel:
    """
    Wrapper for the YOLO-based food classification model.

    Loads a pre-trained YOLO model and provides a method to predict food items
    from uploaded images. Returns the predicted food name along with a confidence score.
    """

    def __init__(self):
        """
        Initialize the Thermitrack YOLO model.

        Loads the YOLO model from the 'classification_models' directory relative
        to the current file. Raises FileNotFoundError if the model file is missing.
        """
        model_path = os.path.join(
            os.path.dirname(__file__), "classification_models", "thermitrack.pt"
        )
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"YOLO model not found at {model_path}")

        self.model = YOLO(model_path)
        logger.info(f"Loaded YOLO model from {model_path}")

    def predict_food(self, image_input: Union[BinaryIO, str]) -> dict:
        """
        Predict the food item in an uploaded image.

        Args:
            image_input (BinaryIO or str): A file-like object containing the uploaded
                image, or a path to an image file.

        Returns:
            dict: {
                "Food": str, Predicted food label,
                "Confidence Score": float, Prediction confidence score
            }

        Raises:
            ValueError: If the image cannot be opened or prediction fails.
        """
        try:
            # Open the image depending on input type
            if hasattr(image_input, "seek"):
                image_input.seek(0)
                img = Image.open(image_input).convert("RGB")
            else:
                img = Image.open(image_input).convert("RGB")
        except (UnidentifiedImageError, Exception) as e:
            logger.error(f"Failed to open image: {e}")
            raise ValueError("Invalid image file provided") from e

        try:
            # Run YOLO prediction
            result = self.model(img)

            # Extract top prediction
            top_index = result[0].probs.top1
            food_name = result[0].names[top_index]
            confidence = float(result[0].probs.top1conf)

            return {"Food": food_name, "Confidence Score": confidence}
        except Exception as e:
            logger.error(f"YOLO prediction failed: {e}")
            raise ValueError("Prediction failed") from e
