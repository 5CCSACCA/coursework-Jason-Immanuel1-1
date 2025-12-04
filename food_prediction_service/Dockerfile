FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV YOLO_CONFIG_DIR=/app/.yolo

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy app code
COPY app/ .

# Copy Firebase key
COPY app/firebase_database/firebase_key.json /app/firebase-key.json

# Create additional directories
RUN mkdir -p /app/.yolo /app/sqlite_database

# Set ownership for non-root user
RUN chown -R appuser:appuser /app/firebase-key.json /app/.yolo /app/sqlite_database /app

# Switch to non-root user
USER appuser

# Expose port for FastAPI
EXPOSE 8000

# Default command for FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


