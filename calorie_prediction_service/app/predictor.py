import subprocess
import re


class BitNetCaloriePredictor:
    """
    Wrapper for the BitNet calorie prediction model.

    Uses an external Python script to perform inference on a given food label
    and returns the estimated calorie count.
    """

    def __init__(self):
        """
        Initialize the predictor with model path and working directory.
        """
        self.model_path = "/bitnet/models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"
        self.bitnet_dir = "/bitnet"

    def predict_calories(self, food_label: str) -> int:
        """
        Predict the number of calories for a given food label.

        Args:
            food_label (str): Name of the food item to estimate calories for.

        Returns:
            int: Estimated calorie count.

        Raises:
            Exception: If the external inference script fails.
            ValueError: If no numeric calorie value is found in the output.
        """
        prompt = f"How many calories are in {food_label}? Answer with just the number."

        result = subprocess.run(
            [
                "python", "run_inference.py",
                "-m", self.model_path,
                "-p", prompt,
                "-n", "50",
            ],
            cwd=self.bitnet_dir,
            capture_output=True,
            text=True,
            timeout=30  # Prevent hanging indefinitely
        )

        if result.returncode != 0:
            raise Exception(f"Inference failed: {result.stderr.strip()}")

        return self._extract(result.stdout)

    def _extract(self, text: str) -> int:
        """
        Extract the first integer from the model output.

        Args:
            text (str): Raw output from the inference script.

        Returns:
            int: Extracted calorie value.

        Raises:
            ValueError: If no numeric value is found in the output.
        """
        # Remove logs or extra content appended by runtime scripts
        text = re.split(r'llama_perf_', text)[0]

        # Extract all integers
        nums = re.findall(r"\d+", text)
        if nums:
            return int(nums[0])

        raise ValueError(f"No calories found in output: {text}")


if __name__ == "__main__":
    predictor = BitNetCaloriePredictor()
    print(predictor.predict_calories("pizza"))

