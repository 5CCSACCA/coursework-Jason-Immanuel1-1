import pytest
from unittest.mock import patch, MagicMock
from calorie_prediction_service.app.predictor import BitNetCaloriePredictor


def test_extract_returns_integer():
    predictor = BitNetCaloriePredictor()
    output_samples = [
        "The answer is 250 calories",
        "123 kcal",
        "Calories: 99 llama_perf_xyz",
        "Approx 500 kcal"
    ]

    for text in output_samples:
        result = predictor._extract(text)
        assert isinstance(result, int)


def test_extract_no_number_raises():
    predictor = BitNetCaloriePredictor()
    with pytest.raises(ValueError):
        predictor._extract("No numbers here")


@patch("subprocess.run")
def test_predict_calories_returns_integer(mock_run):
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout = "Calories: 123"
    mock_run.return_value = mock_process

    predictor = BitNetCaloriePredictor()
    calories = predictor.predict_calories("burger")
    assert isinstance(calories, int)
    mock_run.assert_called_once()


@patch("subprocess.run")
def test_predict_calories_failure(mock_run):
    mock_process = MagicMock()
    mock_process.returncode = 1
    mock_process.stderr = "Script error"
    mock_run.return_value = mock_process

    predictor = BitNetCaloriePredictor()
    with pytest.raises(Exception) as exc:
        predictor.predict_calories("pizza")
    assert "Inference failed" in str(exc.value)
    mock_run.assert_called_once()
