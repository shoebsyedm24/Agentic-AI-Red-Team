# Agentic AI Red Team Lab

> A personal, end-to-end AI security lab for learning and portfolio development.  
> Multi-agent red team system attacking sandboxed vulnerable AI targets — built with Claude + CrewAI.

[![CI](https://github.com/shoebsyedm24/agentic-ai-red-team/actions/workflows/ci.yml/badge.svg)](https://github.com/shoebsyedm24/agentic-ai-red-team/actions/workflows/ci.yml)

---

## What This Is

This lab simulates a real-world AI red team engagement — entirely on localhost in Docker.
You build deliberately vulnerable AI agent targets, then attack them with specialized red team agents
that are themselves powered by Claude AI.

**What makes this different from typical security labs:**  
Every target is an *agentic* AI system (not just a web app), and every attack exploits
*behavioral* vulnerabilities — prompt injection, jailbreaking, RAG data poisoning, and
agentic privilege escalation. Plus OWASP Juice Shop as a 5th target showing how a compromised
AI assistant can be weaponized against a real web app.

---

## Architecture

```
macOS Host
├── Red Team Agents (CrewAI + Claude Sonnet 4.6)
│   Recon → Prompt Injection → Jailbreak → Data Extraction → Privilege Escalation
│   → Web Attack (Juice Shop) → Report (auto-writes to Obsidian)
│
├── Obsidian Knowledge Base (MITRE ATLAS-organized, MCP-connected)
│   Auto-populated with findings after each campaign
│
└── Docker Sandbox (internal: true — NO internet egress)
    ├── target-chatbot  :8080  — Prompt injection target
    ├── target-rag      :8081  — RAG data poisoning target (ChromaDB)
    ├── target-agent    :8082  — Agentic privilege escalation target
    ├── target-multiagent :8083 — Trust boundary target
    ├── juice-shop      :3000  — OWASP Juice Shop (traditional web target)
    └── target-webagent :8084  — AI assistant wrapping Juice Shop (web attack chain)
```

**Key design**: All target containers use `MockVulnerableLLM` — a rule-based simulator
instead of the real Anthropic API. This keeps the network `internal: true` (no internet),
makes findings deterministic, and costs nothing. The real Anthropic API is used only by
the attacking agents on the host.

---

## Red Team Attack Coverage

| Attack | MITRE ATLAS | Target | Description |
|--------|------------|--------|-------------|
| Direct Prompt Injection | AML.T0054.001 | chatbot | Override system prompt via user message |
| Indirect / RAG Injection | AML.T0054.002 | rag | Poison knowledge base with malicious docs |
| LLM Jailbreaking | AML.T0051 | chatbot | Roleplay, DAN, multi-turn Crescendo |
| System Prompt Extraction | AML.T0057 | chatbot, rag | Extract hidden instructions and credentials |
| Path Traversal | AML.T0040 | agent | Read files outside intended workspace |
| Command Injection | AML.T0040 | agent | Execute arbitrary bash via tool args |
| Trust Boundary Bypass | AML.T0054.002 | multiagent | Inject via untrusted worker output |
| AI-Mediated Web Attack | AML.T0054 + OWASP A1 | webagent | Redirect AI to attack Juice Shop REST APIs |

---

## Quickstart

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Python 3.12+
- Node.js 20+ (for Obsidian MCP plugin)
- [Obsidian](https://obsidian.md)

### Setup

```bash
git clone https://github.com/shoebsyedm24/agentic-ai-red-team.git
cd agentic-ai-red-team

# 1. Configure secrets (DRY_RUN=true by default — safe until you verify wiring)
cp .env.example .env
# Edit .env → add your ANTHROPIC_API_KEY

# 2. Install Python deps
pip install -r requirements.txt

# 3. Build and start Docker targets
bash scripts/start_lab.sh

# 4. Seed the RAG knowledge base
python scripts/seed_rag.py

# 5. Dry run — confirms agents work before spending API tokens
DRY_RUN=true python -m agents.campaign --target chatbot
# Check obsidian-vault/03-Findings/ and audit.log

# 6. Live campaign (set DRY_RUN=false in .env first)
python -m agents.campaign --target chatbot
```

### Obsidian Knowledge Base

1. Open Obsidian → **Open folder as vault** → select `obsidian-vault/`
2. Install Community Plugin: search "claude-code-mcp" → Install & Enable
3. In Claude Code: run `/mcp` → verify `obsidian` shows as connected
4. After a campaign, findings appear in `obsidian-vault/03-Findings/` automatically

---

## Project Structure

```
├── agents/                   # Red team agents (CrewAI)
│   ├── roles/                # 7 specialized agents
│   ├── tools/                # HTTP client, payload library, Obsidian writer, MITRE mapper
│   ├── crew.py               # CrewAI Crew + target-to-agent mapping
│   └── campaign.py           # CLI entry point
├── docker/                   # Sandboxed vulnerable targets
│   ├── shared/mock_llm.py    # MockVulnerableLLM (used by all targets)
│   ├── target-chatbot/       # Prompt injection target
│   ├── target-rag/           # RAG poisoning target
│   ├── target-agent/         # Privilege escalation target
│   ├── target-multiagent/    # Trust boundary target
│   └── target-webagent/      # AI web assistant wrapping Juice Shop
├── obsidian-vault/           # Knowledge base (auto-populated)
│   ├── 01-Learning/          # 8 beginner step-by-step notes
│   ├── 02-Tactics/           # MITRE ATLAS technique reference notes
│   ├── 03-Findings/          # Auto-populated by Report Agent
│   ├── 04-Targets/           # Target architecture profiles
│   └── 05-Reports/           # Campaign summaries
├── pyrit_campaigns/          # PyRIT multi-turn attack campaigns
├── garak_scans/              # Garak automated scanning
├── .claude/                  # Claude Code hooks + MCP config
│   ├── settings.json         # Hook definitions + obsidian MCP server
│   └── hooks/                # pre_bash_safety.sh, post_bash_audit.sh, ...
└── tests/                    # pytest — target health + agent smoke tests
```

---

## Learning Path

The `obsidian-vault/01-Learning/` folder contains 8 beginner-friendly notes
that explain every component from first principles:

| Note | Topic |
|------|-------|
| 01 | What Is Agentic AI? (chatbot vs agent, why autonomy changes threat model) |
| 02 | OWASP Top 10 for Agentic Apps (each risk mapped to a lab target) |
| 03 | MITRE ATLAS Framework (tactics, techniques, kill chains) |
| 04 | Docker Sandbox Design (why `internal: true` is the critical control) |
| 05 | CrewAI Architecture (roles, tasks, sequential process, memory) |
| 06 | Claude Code Hooks & MCP (lifecycle events, stdin JSON, Obsidian sync) |
| 07 | PyRIT Deep Dive (Crescendo multi-turn attacks) |
| 08 | Garak Scanner (150+ probes, REST generator, HTML report) |

---

## Tools & Frameworks Used

| Tool | Purpose |
|------|---------|
| [CrewAI](https://github.com/crewaiinc/crewai) | Multi-agent orchestration |
| [Claude Sonnet 4.6](https://anthropic.com) | AI backbone for attacking agents |
| [PyRIT](https://github.com/Azure/PyRIT) | Multi-turn Crescendo attack campaigns |
| [Garak](https://github.com/NVIDIA/garak) | Automated LLM vulnerability scanning (150+ probes) |
| [ChromaDB](https://www.trychroma.com) | Vector DB for RAG poisoning target |
| [OWASP Juice Shop](https://github.com/juice-shop/juice-shop) | Traditional web target for AI-mediated attacks |
| [Obsidian](https://obsidian.md) | MITRE ATLAS-organized knowledge base |

---

## Security Frameworks Referenced

- [OWASP Top 10 for LLM Applications 2025](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [MITRE ATLAS v5.4](https://atlas.mitre.org/)
- [Agentic Security Scoping Matrix (AWS)](https://aws.amazon.com/blogs/security/)

---

## License

MIT — for learning, portfolio work, and authorized security research only.  
**Never run attacks against systems you do not own or have explicit permission to test.**
