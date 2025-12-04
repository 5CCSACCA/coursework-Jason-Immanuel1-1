from pathlib import Path

import pytest
from food_prediction_service.app.model import ThermitrackModel


def test_model_loads_successfully():
    """
    Ensure the YOLO model loads without crashing.
    """
    model = ThermitrackModel()
    assert model.model is not None


def test_predict_food_with_valid_image_file_path():
    """
    Test prediction using a real image file path.
    """
    model = ThermitrackModel()

    test_dir = Path(__file__).parent
    image_path = str(test_dir / "test_images" / "burger.jpg")

    result = model.predict_food(image_path)

    assert isinstance(result, dict)
    assert "Food" in result
    assert "Confidence Score" in result
    assert isinstance(result["Food"], str)
    assert isinstance(result["Confidence Score"], float)
    assert 0.0 <= result["Confidence Score"] <= 1.0


def test_predict_food_with_invalid_file_path():
    """
    Test prediction with missing file.
    """
    model = ThermitrackModel()

    with pytest.raises(ValueError):
        model.predict_food("not_a_real_image.jpg")


def test_predict_food_with_non_image_file():
    """
    Test prediction when a non-image file is passed.
    """
    model = ThermitrackModel()

    # Get the directory where this test file is located
    test_dir = Path(__file__).parent
    test_images_dir = test_dir / "test_images"
    test_images_dir.mkdir(exist_ok=True)

    dummy_file = test_images_dir / "dummy.txt"

    # Create the dummy file
    with open(dummy_file, "w") as f:
        f.write("this is not an image")

    try:
        # Test with the correct path
        with pytest.raises(ValueError, match="Invalid image file provided"):
            model.predict_food(str(dummy_file))
    finally:
        # Clean up the dummy file after the test
        dummy_file.unlink(missing_ok=True)
