#!/bin/bash

# Get project root directory
PROJECT_ROOT=$(pwd)

# Set environment variables
export USE_GPU=false
export USE_ONNX=false
export PYTHONPATH=$PROJECT_ROOT:$PROJECT_ROOT/api
export MODEL_DIR=src/models
export VOICES_DIR=src/voices/v1_0
export WEB_PLAYER_PATH=$PROJECT_ROOT/web
# Set the espeak data path to your location
export ESPEAK_DATA_PATH=/usr/lib/x86_64-linux-gnu/espeak-data

# Run FastAPI with CPU extras using uv run
# Note: espeak may still require manual installation,
uv pip install -e ".[cpu]"
uv run --no-sync python docker/scripts/download_model.py --output api/src/models/v1_0

# Apply the misaki patch to fix possible EspeakWrapper issue in older versions
# echo "Applying misaki patch..."
# python scripts/fix_misaki.py

# Start the server
uv run --no-sync uvicorn api.src.main:app --host 0.0.0.0 --port 8880
