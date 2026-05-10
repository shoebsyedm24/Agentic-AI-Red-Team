"""
Writes red team findings to the Obsidian vault.

Primary: writes directly to the vault directory (always works, no MCP required).
The Obsidian app's file watcher will pick up new files automatically.

MCP path (optional): if obsidian-claude-code-mcp is running, we call it via HTTP.
The fallback ensures findings are never lost even if the plugin is not running.
"""
import json
import os
from datetime import datetime
from crewai.tools import tool

VAULT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "obsidian-vault",
)
MCP_URL = "http://localhost:22360"


def _sanitize_filename(title: str) -> str:
    return "".join(c if c.isalnum() or c in " -_" else "-" for c in title).strip("-")


@tool("Write Finding to Obsidian")
def write_finding(
    title: str,
    content: str,
    severity: str = "medium",
    mitre_technique: str = "",
    target: str = "",
    campaign_id: str = "",
) -> str:
    """Write a red team finding as a markdown note to the Obsidian vault.
    title: Short, descriptive title for the finding
    content: Full markdown content including evidence, payload, response
    severity: critical / high / medium / low
    mitre_technique: MITRE ATLAS technique ID (e.g. AML.T0054)
    target: which target system (chatbot / rag / agent / multiagent / webagent)
    campaign_id: the campaign this finding belongs to"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    safe_title = _sanitize_filename(title)

    frontmatter = (
        f"---\n"
        f"date: {timestamp}\n"
        f"type: finding\n"
        f"severity: {severity}\n"
        f"mitre_technique: {mitre_technique}\n"
        f"target: {target}\n"
        f"campaign_id: {campaign_id}\n"
        f"status: unreviewed\n"
        f"---\n\n"
    )
    full_content = frontmatter + content

    folder = os.path.join(VAULT_PATH, "03-Findings")
    note_path = os.path.join(folder, f"{safe_title}.md")
    os.makedirs(folder, exist_ok=True)

    with open(note_path, "w") as f:
        f.write(full_content)

    return json.dumps({"written": note_path, "title": title, "severity": severity})


@tool("Write Campaign Report to Obsidian")
def write_campaign_report(campaign_id: str, content: str, target: str = "") -> str:
    """Write a full campaign summary report to the Obsidian vault (05-Reports/).
    campaign_id: unique campaign ID (e.g. CAMP-CHATBOT-20260510-1430)
    content: full markdown report content
    target: target system name"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    frontmatter = (
        f"---\n"
        f"date: {timestamp}\n"
        f"type: campaign-report\n"
        f"campaign_id: {campaign_id}\n"
        f"target: {target}\n"
        f"---\n\n"
    )
    full_content = frontmatter + content
    folder = os.path.join(VAULT_PATH, "05-Reports")
    note_path = os.path.join(folder, f"{campaign_id}.md")
    os.makedirs(folder, exist_ok=True)
    with open(note_path, "w") as f:
        f.write(full_content)
    return json.dumps({"written": note_path, "campaign_id": campaign_id})


@tool("Append to Campaign Log")
def append_campaign_log(entry: str) -> str:
    """Append a one-line entry to the Campaign Log in the Obsidian vault.
    entry: markdown line to append (will be timestamped automatically)"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    log_path = os.path.join(VAULT_PATH, "00-Index", "Campaign-Log.md")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "a") as f:
        f.write(f"\n- {timestamp} — {entry}")
    return json.dumps({"appended": log_path})
