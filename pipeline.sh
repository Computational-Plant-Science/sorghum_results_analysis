#!/usr/bin/env bash
# pipeline.sh — Build once, then run clean or any .py script via container ENTRYPOINT

set -euo pipefail

IMAGE_NAME="trait-pipeline"
DOCKERFILE="Dockerfile"
HOST_DATA_DIR="$(pwd)/data"
CTR_DATA_DIR="/srv/data"

# 1️⃣ Build image if it doesn't already exist
if ! docker image inspect "${IMAGE_NAME}" &>/dev/null; then
  echo "🔨 Building Docker image '${IMAGE_NAME}'..."
  docker build --platform linux/amd64 -t "${IMAGE_NAME}" -f "${DOCKERFILE}" .
else
  echo "✅ '${IMAGE_NAME}' exists, skipping build."
fi

# 2️⃣ Ensure data dir on host
mkdir -p "${HOST_DATA_DIR}"

# 3️⃣ Decide what to run:
#    - no args      → clean
#    - first arg .py → run that script
if [[ $# -eq 0 ]]; then
  MODE="clean"
else
  FIRST="$1"
  if [[ "${FIRST}" == "clean" ]]; then
    MODE="clean"
    shift
  elif [[ "${FIRST}" == *.py ]]; then
    MODE="run"
    SCRIPT="${FIRST}"
    shift
  else
    echo "❌ Unknown command: '${FIRST}'"
    echo "Usage:"
    echo "  $0            # clean"
    echo "  $0 clean      # same as no args"
    echo "  $0 script.py  # run any Python script"
    exit 1
  fi
fi

# 4️⃣ Run via container ENTRYPOINT (python3 is default entrypoint)
case "${MODE}" in
  clean)
    echo "🧼 [clean] Combining & cleaning data…"
    docker run --rm \
      -v "${HOST_DATA_DIR}:${CTR_DATA_DIR}" \
      "${IMAGE_NAME}" \
      combine_and_clean_data.py \
        --input-dir "${CTR_DATA_DIR}/raw" \
        --metadata "${CTR_DATA_DIR}/meta.xlsx" \
        --output "${CTR_DATA_DIR}/cleaned.xlsx"
    echo "✅ cleaned → ./data/cleaned.xlsx"
    ;;

  run)
    echo "🚀 [run] ${SCRIPT} with args: $*"
    docker run --rm \
      -v "${HOST_DATA_DIR}:${CTR_DATA_DIR}" \
      "${IMAGE_NAME}" \
      "${SCRIPT}" "$@"
    ;;
esac
