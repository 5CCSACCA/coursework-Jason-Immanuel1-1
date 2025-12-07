# Food Prediction Service (SaaS)

**Coursework for 5CCSACCA – Cloud Computing for Artificial Intelligence**  
**Author:** Jason Immanuel

This project is a SaaS application that provides a food image prediction service using machine learning. It includes:

- A live API for image-based food prediction
- Unit and live API tests
- Containerization using Docker and Docker Compose for easy deployment
- Integration with Firebase for authentication

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [API Endpoints](#api-endpoints)
- [Running Tests](#running-tests)
- [Running Live API Tests](#running-live-api-tests)
- [Notes and Known Issues](#notes-and-known-issues)

## Prerequisites

Ensure your Linux machine has the following installed:

- **Docker & Docker Compose** ([Installation guide](https://docs.docker.com/get-docker/))
- **Python 3.11**
- Internet access to download Python dependencies

## Project Structure

```
coursework-Jason-Immanuel1-1/
├── food_prediction_service/       # Main SaaS service code
│   ├── app/
│   │   ├── authentication.py      # Firebase authentication
│   │   ├── model.py               # YOLO/ML model
│   │   └── firebase_database/     # Firebase database client & key
├── tests/                         # Unit and live API tests
│   └── requirements.txt           # Python dependencies for testing
├── run_tests.sh                   # Script to run all tests automatically
├── docker-compose.yml             # Docker Compose configuration
└── README.md                      # This README
```

## Setup Instructions (Linux)

### 1. Clone the repository

```bash
git clone https://github.com/5CCSACCA/coursework-Jason-Immanuel1-1
cd coursework-Jason-Immanuel1-1
```

### 2. Build and start the SaaS project using Docker Compose

```bash
docker compose build
docker compose up
```

This builds all Docker images and starts the project services.

## API Endpoints

### POST /predict
Submits an image for food prediction.

**Example Output:**
```json
{
  "results": [
    {
      "id": "eQqJdL4nuH8XBrcDfIzA",
      "prediction": {
        "Food": "pizza",
        "Confidence Score": 0.9999982118606567
      },
      "filename": "pizza.jpg"
    }
  ]
}
```

### GET /predictions
Retrieves all predictions for the authenticated user.

**Example Output:**
```json
{
  "predictions": [
    {
      "userId": "IgMEVA88fPdSnIfiyvkNUfCCcDM2",
      "confidence": 0.9709324836730957,
      "prediction": "hamburger",
      "calories": 450,
      "filename": "crispy-comte-cheesburgers-FT-RECIPE0921-6166c6552b7148e8a8561f7765ddf20b.jpg",
      "id": "79lpgP7crRf4BGBRuH2h"
    }
  ]
}
```

### PUT /predictions/{doc_id}
Updates a specific prediction by document ID.

**Example Output:**
```json
{
  "status": "updated"
}
```

### DELETE /predictions/{doc_id}
Deletes a specific prediction by document ID.

**Example Output:**
```json
{
  "status": "deleted"
}
```

## Running Tests

### 1. Install Python virtual environment support
```bash
sudo apt install python3.11-venv
```

### 2. Make the test script executable and run it
```bash
chmod +x run_tests.sh
./run_tests.sh
```

The script will automatically create the virtual environment and install all dependencies from `tests/requirements.txt` before running the tests.


## Running Live API Tests

### 1. Make sure the SaaS project is running via Docker Compose

```bash
docker compose up
```

### 2. Navigate to the tests folder

```bash
cd tests
```

### 3. Run the live API tests

```bash
python3 live_api_test.py
```

This tests the live endpoints of the SaaS, including authentication and model predictions.

## Notes and Known Issues

- **Firebase Credentials:** Ensure `food_prediction_service/app/firebase_database/firebase_key.json` exists and contains valid credentials for tests requiring Firebase authentication.

- **Linux VM Restrictions:** If `pip` fails to install packages system-wide, always use a virtual environment (`venv`) to avoid permission issues.

- **Docker Requirements:** Docker must be running before starting the SaaS with `docker compose up`.

- **Cross-Platform:** This guide is tailored for Linux. Windows users may need PowerShell-specific adjustments.

- **SaaS Context:** The service is designed to be deployable as a cloud-hosted SaaS application.
