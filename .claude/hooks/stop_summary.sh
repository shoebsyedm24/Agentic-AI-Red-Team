#!/usr/bin/env bash
# Stop hook — appends a session-end marker to audit.log
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_FILE="/Users/shoeb/Documents/Agentic AI Red Teaming/agentic-ai-red-team/audit.log"
echo "${TIMESTAMP} | SESSION_END | Claude Code session ended" >> "$LOG_FILE"
echo "Session ended. Audit log: $LOG_FILE"
exit 0
