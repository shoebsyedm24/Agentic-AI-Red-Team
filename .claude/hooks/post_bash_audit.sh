#!/usr/bin/env bash
# Post-Bash audit hook
# Appends every executed bash command to audit.log with a UTC timestamp.
# This creates an immutable record of all commands run during the session.

INPUT=$(cat)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', '<unknown>'))
except Exception:
    print('<parse error>')
" 2>/dev/null)

LOG_FILE="/Users/shoeb/Documents/Agentic AI Red Teaming/agentic-ai-red-team/audit.log"
echo "${TIMESTAMP} | BASH | ${COMMAND}" >> "$LOG_FILE"
exit 0
