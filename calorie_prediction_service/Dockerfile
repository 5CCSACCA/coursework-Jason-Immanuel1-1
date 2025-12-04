# Build BitNet
FROM python:3.11-slim AS build

# Set working directory
WORKDIR /bitnet

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    clang \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Clone BitNet repository
RUN git clone --recursive https://github.com/microsoft/BitNet.git .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt huggingface_hub

# Download the pre-trained BitNet model from HuggingFace
RUN huggingface-cli download microsoft/BitNet-b1.58-2B-4T-gguf --local-dir models/BitNet-b1.58-2B-4T

# Setup environment for BitNet
RUN python setup_env.py -md models/BitNet-b1.58-2B-4T -q i2_s

# Build the BitNet binaries
RUN mkdir -p build && cd build && cmake .. && make -j$(nproc)

# Runtime environment
FROM python:3.11-slim

# Set working directory for the app
WORKDIR /app

# Copy BitNet build artifacts from build stage
COPY --from=build /bitnet /bitnet

# Install Python dependencies for the app
COPY calorie_prediction_service/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY calorie_prediction_service /app

# Ensure BitNet binary is executable
RUN chmod +x /bitnet/build/bin/llama-cli

# Environment variables for BitNet
ENV BITNET_DIR=/bitnet
ENV MODEL_PATH=/bitnet/models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf

# Set default command to run the consumer
CMD ["python", "app/consumer.py"]

