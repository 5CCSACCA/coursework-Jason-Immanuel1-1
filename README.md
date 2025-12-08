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

## Installation

### 1. Update your system
```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Git
```bash
sudo apt install git -y
git --version
```

### 3. Install Docker (official Docker version)

Remove any old Docker first:
```bash
sudo apt remove docker docker.io docker-ce docker-ce-cli containerd runc -y
```

Install Docker using the official convenience script:
```bash
curl -fsSL https://get.docker.com | sh
```

Start Docker and enable it on boot:
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

Add your user to the docker group so you don't need sudo:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

> **Note:** You may need to log out and log back in for the group changes to take effect.

Check Docker:
```bash
docker --version
docker run hello-world
```

> **Security Note:** Adding your user to the docker group grants privileges equivalent to root access. For enhanced security in production environments, consider using [Docker rootless mode](https://docs.docker.com/go/rootless/).

### 4. Install Docker Compose (modern integrated CLI)

With the official Docker install, you can now use the new CLI:
```bash
docker compose version
```

If it's missing, install the plugin manually:
```bash
sudo apt install docker-compose-plugin -y
docker compose version
```

### 5. Clone the repository
```bash
git clone https://github.com/5CCSACCA/coursework-Jason-Immanuel1-1
cd coursework-Jason-Immanuel1-1
```

## Usage

### Build and start the SaaS project using Docker Compose
```bash
docker compose build
docker compose up
```

To run in detached mode:
```bash
docker compose up -d
```

To stop the services:
```bash
docker compose down
```
> **Troubleshooting:** 
> - If you encounter permission errors with Docker commands, you may need to use `sudo` before each command (e.g., `sudo docker compose up`) or log out and log back in for the docker group changes to take effect.
> - If you hit Docker Hub rate limits, log in with your Docker Hub account:
>   ```bash
>   docker login
>   ```

## API Endpoints

## GET /interactions
Retrieves all API interactions for the authenticated user.

**Example Output:**
```json
{
  "interactions": [
    {
      "id": 1,
      "endpoint": "/predict",
      "method": "POST",
      "timestamp": "2025-12-07T20:06:32.349183"
    }
  ]
}
```

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
      "filename": "burger.jpg",
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

The project includes automated tests that can be run with a single command.

### Prerequisites for Testing

Install Python virtual environment support:
```bash
sudo apt install python3.11-venv
```

### Run All Tests

Make the test script executable and run it:
```bash
chmod +x run_tests.sh
./run_tests.sh
```

The script will automatically:
- Create a virtual environment
- Install all dependencies from `tests/requirements.txt`
- Run all tests including live API tests

**Note:** Make sure the SaaS project is running via Docker Compose before running the tests.


## Notes and Known Issues

- **Firebase Credentials:** Ensure `food_prediction_service/app/firebase_database/firebase_key.json` exists and contains valid credentials for tests requiring Firebase authentication.

- **Linux VM Restrictions:** If `pip` fails to install packages system-wide, always use a virtual environment (`venv`) to avoid permission issues.

- **Docker Requirements:** Docker must be running before starting the SaaS with `docker compose up`.

- **Cross-Platform:** This guide is tailored for Linux. Windows users may need PowerShell-specific adjustments.

- **SaaS Context:** The service is designed to be deployable as a cloud-hosted SaaS application.
