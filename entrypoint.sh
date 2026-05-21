#!/usr/bin/env bash
set -eo pipefail

echo "[Infra] Checking NVIDIA GPU Infrastructure..."
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ ERROR: NVIDIA Driver/CUDA is not exposed to this layer."
    exit 1
fi
nvidia-smi

echo "[Infra] Launching vLLM Engine Engine via Docker Compose..."
docker-compose -f docker-compose.yml up -d

echo "[Infra] Awaiting OpenAI-compatible API Endpoint (Port 8000)..."
until curl -s http://localhost:8000/v1/models > /dev/null; do
    sleep 5
    echo "... Booting llm weights into VRAM ..."
done

echo "✅ vLLM Engine is fully initialized and operational."
