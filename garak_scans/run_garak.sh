#!/usr/bin/env bash
# Run a Garak automated LLM vulnerability scan against a target container.
#
# Usage:
#   bash garak_scans/run_garak.sh chatbot
#   bash garak_scans/run_garak.sh rag
#
# Prerequisites:
#   pip install garak
#   Lab must be running: bash scripts/start_lab.sh

set -euo pipefail

TARGET="${1:-chatbot}"
REPORT_DIR="$(dirname "$0")/reports"
mkdir -p "$REPORT_DIR"
TIMESTAMP=$(date +%Y%m%d-%H%M)

declare -A PORTS=(
  ["chatbot"]="8080"
  ["rag"]="8081"
  ["agent"]="8082"
  ["multiagent"]="8083"
  ["webagent"]="8084"
)

declare -A ENDPOINTS=(
  ["chatbot"]="/chat"
  ["rag"]="/query"
  ["agent"]="/run"
  ["multiagent"]="/orchestrate"
  ["webagent"]="/ask"
)

declare -A MESSAGE_KEYS=(
  ["chatbot"]="message"
  ["rag"]="query"
  ["agent"]="task"
  ["multiagent"]="task"
  ["webagent"]="message"
)

PORT="${PORTS[$TARGET]}"
ENDPOINT="${ENDPOINTS[$TARGET]}"
MSG_KEY="${MESSAGE_KEYS[$TARGET]}"
TARGET_URL="http://localhost:${PORT}${ENDPOINT}"
REPORT_PREFIX="$REPORT_DIR/${TARGET}-${TIMESTAMP}"

echo "=== Garak Scan: target-${TARGET} ==="
echo "URL: $TARGET_URL"
echo "Report: ${REPORT_PREFIX}.html"
echo ""

# Check target is up
if ! curl -sf --max-time 5 "http://localhost:${PORT}/health" > /dev/null 2>&1; then
  echo "ERROR: target-${TARGET} is not running on port ${PORT}"
  echo "Start the lab: bash scripts/start_lab.sh"
  exit 1
fi

# Check garak is installed
if ! command -v garak &> /dev/null; then
  echo "ERROR: garak not installed. Install with: pip install garak"
  exit 1
fi

echo "Starting Garak scan..."
garak \
  --model_type rest \
  --model_name "target-${TARGET}" \
  --generator_option "uri=${TARGET_URL}" \
  --generator_option "request_template={\"${MSG_KEY}\": \"{prompt}\"}" \
  --generator_option "response_path=response" \
  --probes "probes.prompt_injection,probes.dan,probes.encoding,probes.leakage" \
  --report_prefix "$REPORT_PREFIX" \
  2>&1

echo ""
echo "Scan complete."
echo "HTML report: ${REPORT_PREFIX}.html"
echo "Open with: open ${REPORT_PREFIX}.html"
