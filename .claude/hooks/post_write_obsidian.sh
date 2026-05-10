#!/usr/bin/env bash
# Post-Write hook
# When Claude Code writes a file inside obsidian-vault/, log it to audit.log.
# Obsidian's file watcher picks up new files automatically — no extra sync needed.

INPUT=$(cat)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('file_path', '') or d.get('tool_input', {}).get('path', ''))
except Exception:
    print('')
" 2>/dev/null)

LOG_FILE="/Users/shoeb/Documents/Agentic AI Red Teaming/agentic-ai-red-team/audit.log"

if echo "$FILE_PATH" | grep -q "obsidian-vault"; then
    echo "${TIMESTAMP} | OBSIDIAN_WRITE | ${FILE_PATH}" >> "$LOG_FILE"
fi
exit 0
