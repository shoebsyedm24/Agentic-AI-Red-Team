#!/usr/bin/env bash
# Pre-Bash safety hook
# Reads tool input JSON from stdin. Exits with code 2 to BLOCK, 0 to ALLOW.
#
# What this blocks:
#   - SSH or curl/wget to external hosts (anything not localhost)
#   - docker exec modifications inside target containers
#
# Why: Prevents Claude Code from accidentally sending real attack traffic
# to external systems or modifying the sandbox environment unexpectedly.

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', ''))
except Exception:
    print('')
" 2>/dev/null)

# Block SSH to any host
if echo "$COMMAND" | grep -qE '^[[:space:]]*ssh[[:space:]]'; then
    echo "BLOCKED by pre_bash_safety.sh: SSH is not permitted in this project." >&2
    echo "All attacks must go through localhost Docker targets." >&2
    exit 2
fi

# Block curl/wget to non-localhost URLs
if echo "$COMMAND" | grep -qP '(curl|wget).*https?://(?!(localhost|127\.0\.0\.1|0\.0\.0\.0))'; then
    echo "BLOCKED by pre_bash_safety.sh: External HTTP requests are not permitted." >&2
    echo "Target containers run on localhost:8080-8084." >&2
    exit 2
fi

# Block docker exec into target containers with destructive flags
if echo "$COMMAND" | grep -qE 'docker[[:space:]]+exec.*(target-|juice-shop).*(rm|chmod 777|chown root|mkfs)'; then
    echo "BLOCKED by pre_bash_safety.sh: Destructive docker exec into target containers is not permitted." >&2
    exit 2
fi

# Allow everything else
exit 0
