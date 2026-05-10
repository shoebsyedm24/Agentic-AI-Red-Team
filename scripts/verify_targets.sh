#!/usr/bin/env bash
# Health-check all target containers and print a status table.
# Exit code 0 if all pass, 1 if any fail.

set -uo pipefail

declare -A TARGETS=(
  ["target-chatbot"]="http://localhost:8080/health"
  ["target-rag"]="http://localhost:8081/health"
  ["target-agent"]="http://localhost:8082/health"
  ["target-multiagent"]="http://localhost:8083/health"
  ["juice-shop"]="http://localhost:3000/rest/admin/application-version"
  ["target-webagent"]="http://localhost:8084/health"
)

PASS=0
FAIL=0

echo ""
echo "Target Health Check"
echo "────────────────────────────────────────"
printf "%-20s %-10s %s\n" "Service" "Status" "URL"
echo "────────────────────────────────────────"

for name in "${!TARGETS[@]}"; do
  url="${TARGETS[$name]}"
  if curl -sf --max-time 5 "$url" > /dev/null 2>&1; then
    printf "%-20s %-10s %s\n" "$name" "✓ OK" "$url"
    ((PASS++)) || true
  else
    printf "%-20s %-10s %s\n" "$name" "✗ FAIL" "$url"
    ((FAIL++)) || true
  fi
done

echo "────────────────────────────────────────"
echo "Passed: $PASS / $((PASS + FAIL))"

if [[ $FAIL -gt 0 ]]; then
  echo "Some targets are not ready. Wait a few seconds and retry, or check:"
  echo "  docker compose -f docker/docker-compose.yml logs"
  exit 1
fi

echo "All targets healthy."
