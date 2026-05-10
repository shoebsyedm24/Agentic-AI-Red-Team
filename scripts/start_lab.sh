#!/usr/bin/env bash
# Start all Docker targets and verify they are healthy
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Starting Agentic AI Red Team Lab ==="
echo ""

# Check .env exists
if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
  echo "ERROR: .env not found. Copy .env.example to .env and add your ANTHROPIC_API_KEY."
  exit 1
fi

# Load env vars for docker compose
set -o allexport
source "$PROJECT_ROOT/.env"
set +o allexport

echo "[1/3] Building Docker images (first run may take a few minutes)..."
docker compose -f "$PROJECT_ROOT/docker/docker-compose.yml" build --quiet

echo "[2/3] Starting containers..."
docker compose -f "$PROJECT_ROOT/docker/docker-compose.yml" up -d

echo "[3/3] Verifying targets are healthy..."
bash "$SCRIPT_DIR/verify_targets.sh"

echo ""
echo "Lab is running. To stop: bash scripts/stop_lab.sh"
