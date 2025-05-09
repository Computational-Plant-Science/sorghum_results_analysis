#!/usr/bin/env bash
# Enhanced runner for both data cleaning and plotting scripts

set -euo pipefail

IMAGE_NAME="trait-pipeline"
DOCKERFILE="Dockerfile"
HOST_DATA_DIR="$(pwd)/data"
CTR_DATA_DIR="/srv/data"

# Build the image
echo "🔨 Building Docker image '${IMAGE_NAME}'..."
docker build --platform linux/amd64 -t "${IMAGE_NAME}" -f "${DOCKERFILE}" .

# If no args are passed, default to running combine_and_clean_data.py
if [[ $# -eq 0 ]]; then
  echo "🚀 Running data cleaning (combine_and_clean_data.py)..."
  docker run --rm -it \
    -v "${HOST_DATA_DIR}:${CTR_DATA_DIR}" \
    "${IMAGE_NAME}" \
      python3 combine_and_clean_data.py \
        --input-dir "${CTR_DATA_DIR}/raw" \
        --metadata "${CTR_DATA_DIR}/meta.xlsx" \
        --output "${CTR_DATA_DIR}/cleaned.xlsx"
  echo "✅ cleaned.xlsx generated at ./data/cleaned.xlsx"

# If args are passed, treat the first arg as the script, and the rest as arguments
else
  SCRIPT="$1"
  shift
  echo "🚀 Running custom script: ${SCRIPT}"
  echo "    with arguments: $*"
  docker run --rm -it \
    -v "${HOST_DATA_DIR}:${CTR_DATA_DIR}" \
    "${IMAGE_NAME}" \
      python3 "${SCRIPT}" "$@"
fi
