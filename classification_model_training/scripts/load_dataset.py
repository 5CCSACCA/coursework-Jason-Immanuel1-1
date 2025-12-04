import os
from typing import List, Dict, Any
from datasets import load_dataset


class DatasetBuilder:
    """
    Utility class for downloading, processing, and exporting datasets
    into a YOLO-compatible directory structure.

    This class supports:
    - Downloading datasets from Hugging Face
    - Extracting labels
    - Saving images into train/validation folders
    - Creating a YOLO `data.yaml` configuration file
    """

    def __init__(self, dataset_name: str) -> None:
        """
        Initialize the dataset builder.

        Args:
            dataset_name (str): The Hugging Face dataset identifier
                (e.g., "ethz/food101").
        """
        self.dataset_name: str = dataset_name
        self.dataset: Dict[str, Any] | None = None

    def load_dataset(self) -> Dict[str, Any]:
        """
        Load the dataset from Hugging Face.

        Returns:
            dict: Loaded dataset object.

        Raises:
            Exception: If the dataset cannot be downloaded or initialized.
        """
        self.dataset = load_dataset(self.dataset_name)
        print("Dataset loaded successfully.")
        return self.dataset

    def _get_labels(self) -> List[str]:
        """
        Extract class label names from the dataset.

        Returns:
            List[str]: List of label names.

        Raises:
            ValueError: If the dataset has not been loaded.
        """
        if self.dataset is None:
            raise ValueError("Dataset not loaded. Call load_dataset() first.")

        return self.dataset["train"].features["label"].names

    def save_dataset(self, base_dir: str = "../dataset") -> None:
        """
        Save dataset images into a YOLO-compatible folder structure.

        Structure:
            base_dir/
                train/
                    class_name/
                validation/
                    class_name/

        Args:
            base_dir (str): Base output directory for dataset storage.

        Raises:
            ValueError: If the dataset has not been loaded.
        """
        if self.dataset is None:
            raise ValueError("Dataset not loaded. Call load_dataset() first.")

        for split in ["train", "validation"]:
            dataset_split = self.dataset[split]

            for index, sample in enumerate(dataset_split):
                image = sample["image"]
                label_id = sample["label"]

                # Convert numeric label to class name
                label_name = dataset_split.features["label"].int2str(label_id)

                # Create output directory for this class
                save_dir = os.path.join(base_dir, split, label_name)
                os.makedirs(save_dir, exist_ok=True)

                # Save image using a stable naming pattern
                image_path = os.path.join(save_dir, f"{index}-{split}.jpg")
                image.save(image_path)

        print("Dataset saved successfully.")

    def create_yaml(self, base_dir: str = "../dataset") -> None:
        """
        Create a YOLO-compatible `data.yaml` file.

        The YAML file defines:
        - Dataset root path
        - Train/validation directories
        - Class index-to-name mappings

        Args:
            base_dir (str): Base dataset directory where YAML is saved.

        Raises:
            ValueError: If the dataset has not been loaded.
        """
        labels = self._get_labels()

        yaml_content = f"""path: {base_dir}
train: train
val: validation

names:
"""

        for i, label in enumerate(labels):
            yaml_content += f"  {i}: {label}\n"

        yaml_path = os.path.join(base_dir, "data.yaml")
        with open(yaml_path, "w", encoding="utf-8") as f:
            f.write(yaml_content)

        print(f"YOLO data.yaml created at: {yaml_path}")

    def create_dataset(self) -> None:
        """
        Full pipeline to create a YOLO-ready dataset:
        1. Load dataset
        2. Save images to disk
        3. Generate `data.yaml`
        """
        self.load_dataset()
        self.save_dataset()
        self.create_yaml()


if __name__ == "__main__":
    dataset = DatasetBuilder("ethz/food101")
    dataset.create_dataset()

