#!/bin/bash
set -e

echo "Running Tests for Food Prediction SaaS"

# Check if virtual environment exists; create if not
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies from requirements.txt
if [ -f "tests/requirements.txt" ]; then
    echo "Installing project dependencies..."
    pip install -r tests/requirements.txt
else
    echo "Error: tests/requirements.txt not found."
    exit 1
fi

# Run pytest for unit tests
echo "Running all unit tests..."
python -m pytest -v
echo "Unit tests completed."

# Run the live API test script
LIVE_API_SCRIPT="tests/live_api_test.py"
if [ -f "$LIVE_API_SCRIPT" ]; then
    echo "Running live API tests..."
    python "$LIVE_API_SCRIPT"
    echo "Live API tests completed."
else
    echo "Error: $LIVE_API_SCRIPT not found."
    exit 1
fi

echo "All tests finished successfully."

