#!/bin/bash

set -e

if ! command -v python3 &> /dev/null
then
    echo "python3 not found. Install Python 3."
    exit 1
fi

if ! python3 -m pytest --version &> /dev/null
then
    echo "pytest not found. Installing..."
    python3 -m pip install --upgrade pip
    python3 -m pip install pytest
    echo "pytest installed successfully."
fi

echo "Running tests..."
python3 -m pytest -v .
