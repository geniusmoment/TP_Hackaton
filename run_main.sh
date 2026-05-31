#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN="$SCRIPT_DIR/main.py"
ARCHIVE="$SCRIPT_DIR/inbox.zip"
LOG_FILE="$SCRIPT_DIR/classification.log"

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
python "$MAIN" "$ARCHIVE" 2>&1 | tee
echo "=== [$(date '+%Y-%m-%d %H:%M:%S')] Processing completed successfully ===" | tee -a "$LOG_FILE"