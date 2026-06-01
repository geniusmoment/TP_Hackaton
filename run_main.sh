#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN="$SCRIPT_DIR/main.py"
ARCHIVE="$SCRIPT_DIR/inbox.zip"
LOG_FILE="$SCRIPT_DIR/classification.log"

export OPENAI_API_KEY=""
export OPENAI_BASE_URL="https://api.openai.com/v1"

USE_AI_FLAG=""
if [ "$1" == "--use-ai" ]; then
    USE_AI_FLAG="--use-ai"
fi

echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] Starting email classification ===" | tee -a "$LOG_FILE"

if [ ! -f "$MAIN" ]; then
    echo "Error: Script file $MAIN not found!" | tee -a "$LOG_FILE"
    exit 1
fi

if [ ! -f "$ARCHIVE" ]; then
    echo "Error: Email archive $ARCHIVE not found!" | tee -a "$LOG_FILE"
    exit 1
fi

echo "Processing archive: $ARCHIVE" | tee -a "$LOG_FILE"
if [ ! -z "$USE_AI_FLAG" ]; then
    echo "Using AI-based classification." | tee -a "$LOG_FILE"
else
    echo "Using rule-based classification." | tee -a "$LOG_FILE"
fi
python "$MAIN" "$ARCHIVE" $USE_AI_FLAG 2>&1 | tee -a "$LOG_FILE"
echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] Processing completed successfully ===" | tee -a "$LOG_FILE"