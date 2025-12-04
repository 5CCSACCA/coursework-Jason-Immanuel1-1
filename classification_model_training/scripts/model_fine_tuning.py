from ultralytics import YOLO
import os
import glob
import shutil
from typing import Optional


class FineTuning:
    """
    Handles fine-tuning of a YOLO classification model and saving the best checkpoint.

    This class:
    - Loads a pre-trained YOLO classification model
    - Trains it on a custom dataset
    - Automatically locates and saves the best model checkpoint
    """

    def __init__(self, model_name: str, save_path: str = "/models/food_classifier.pt"):
        """
        Initialize the fine-tuning pipeline.

        Args:
            model_name (str): Path or name of the base YOLO classification model.
            save_path (str): Destination path for the best trained model.
        """
        self.model_name = model_name
        self.save_path = save_path

        # Ensure output directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

    def train_model(
        self,
        data: str = "../dataset",
        epochs: int = 100,
        imgsz: int = 640,
        device: Optional[int] = 0
    ) -> None:
        """
        Train the YOLO model and save the best performing weights.

        Args:
            data (str): Path to YOLO dataset config file (data.yaml).
            epochs (int): Number of training epochs.
            imgsz (int): Input image resolution.
            device (Optional[int]): CUDA device index. Set to None for CPU.

        Returns:
            None

        Raises:
            FileNotFoundError: If trained model weights cannot be located.
        """
        # Load the base YOLO classification model
        model = YOLO(self.model_name)

        # Start training
        model.train(
            data=data,
            epochs=epochs,
            imgsz=imgsz,
            device=device
        )

        # YOLO saves results under runs/train/exp*
        weights_dir = "runs/train"
        exp_dirs = sorted(
            glob.glob(os.path.join(weights_dir, "exp*")),
            key=os.path.getmtime,
            reverse=True
        )

        if not exp_dirs:
            raise FileNotFoundError("No YOLO training runs found in runs/train directory.")

        # Select the most recent experiment
        latest_exp = exp_dirs[0]
        best_model = os.path.join(latest_exp, "weights", "best.pt")

        if not os.path.exists(best_model):
            raise FileNotFoundError(f"Best model not found at: {best_model}")

        # Copy best model to the final destination
        shutil.copy(best_model, self.save_path)

        print(f"Best model saved to: {self.save_path}")


if __name__ == "__main__":
    trainer = FineTuning("yolo11n-cls.pt")
    trainer.train_model()

