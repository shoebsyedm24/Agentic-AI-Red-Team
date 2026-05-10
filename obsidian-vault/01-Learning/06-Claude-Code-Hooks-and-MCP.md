# 06 — Claude Code Hooks & MCP

## Learning Objectives
- Understand the 5 hook lifecycle events and when each fires
- Know what JSON format hooks receive on stdin
- Understand how MCP connects Claude Code to Obsidian
- Test hooks manually before relying on them

## Prerequisites
[[05-CrewAI-Architecture]]

---

## What Are Claude Code Hooks?

Hooks are shell scripts (or other commands) that Claude Code runs automatically at specific points
in its lifecycle. They run on YOUR machine, not in Docker.

Think of them as event listeners for Claude's actions:

```
User types prompt
    ↓
Claude Code generates a Bash command
    ↓
PreToolUse[Bash] hook fires → runs pre_bash_safety.sh
    ↓ (only if hook exits 0 — allowed)
Bash command executes
    ↓
PostToolUse[Bash] hook fires → runs post_bash_audit.sh
    ↓
Claude Code session ends
    ↓
Stop hook fires → runs stop_summary.sh
```

---

## Hook Configuration (.claude/settings.json)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": "path/to/pre_bash_safety.sh"}]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [{"type": "command", "command": "path/to/post_bash_audit.sh"}]
      },
      {
        "matcher": "Write",
        "hooks": [{"type": "command", "command": "path/to/post_write_obsidian.sh"}]
      }
    ],
    "Stop": [
      {"hooks": [{"type": "command", "command": "path/to/stop_summary.sh"}]}
    ]
  }
}
```

The `matcher` field is the tool name: `"Bash"`, `"Write"`, `"Read"`, etc.

---

## What Hooks Receive (stdin JSON)

Every hook receives a JSON object on stdin describing what's happening:

**PreToolUse / PostToolUse for Bash:**
```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "docker compose -f docker/docker-compose.yml up -d"
  }
}
```

**PostToolUse for Write:**
```json
{
  "tool_name": "Write",
  "tool_input": {
    "file_path": "/path/to/obsidian-vault/03-Findings/Finding.md",
    "content": "---\ndate: 2026-05-10\n..."
  }
}
```

The hooks use Python to parse this:
```bash
COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(d.get('tool_input', {}).get('command', ''))
")
```

---

## Exit Codes: How Hooks Control Behavior

| Exit code | Effect |
|-----------|--------|
| 0 | Allow — tool runs normally |
| 2 | Block — tool is NOT run; stderr shown to user |
| Other | Non-blocking error — tool runs but error is logged |

This is how `pre_bash_safety.sh` blocks dangerous commands:
```bash
if echo "$COMMAND" | grep -qE '^[[:space:]]*ssh[[:space:]]'; then
    echo "BLOCKED: SSH not permitted" >&2
    exit 2   # ← blocks the SSH command
fi
exit 0       # ← allows everything else
```

---

## What MCP Is

MCP (Model Context Protocol) is a standard way for Claude Code to talk to external tools and data sources.

In this project, MCP connects Claude Code to the Obsidian vault:

```
Claude Code (MCP client)
    ↓ tools: obsidian_read_file, obsidian_write_file, obsidian_search
obsidian-claude-code-mcp (MCP server, Node.js)
    ↓ reads/writes
Obsidian Vault (markdown files)
    ↓ file watcher
Obsidian App (displays notes in real time)
```

Once connected, you can tell Claude Code:
"Write a finding note to the vault" and it will call the MCP tool directly
without you needing to run any Python code.

---

## Hands-On Exercise

**Test the safety hook manually:**
```bash
# Simulate a dangerous command
echo '{"tool_name":"Bash","tool_input":{"command":"ssh root@evil.com"}}' \
  | bash .claude/hooks/pre_bash_safety.sh
echo "Exit code: $?"
```
Expected: "BLOCKED" message in stderr, exit code 2.

**Test the audit hook:**
```bash
echo '{"tool_name":"Bash","tool_input":{"command":"docker compose up -d"}}' \
  | bash .claude/hooks/post_bash_audit.sh
cat audit.log
```
Expected: A timestamped line in `audit.log`.

**Check MCP connection:**
In Claude Code terminal, type `/mcp`
Look for `obsidian` in the list with status "connected".

---

## Further Reading
- [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks)
- [MCP Specification](https://modelcontextprotocol.io/)

## Next Step
→ [[07-PyRIT-Deep-Dive]]
