# Agentic AI Red Team Lab

## Purpose
Personal AI security lab for learning and portfolio development.
We build deliberately vulnerable AI agent targets and attack them using
red team agents powered by LLM + CrewAI. All attack activity is
contained within Docker containers on localhost.

GitHub: https://github.com/shoebsyedm24/agentic-ai-red-team

## Safety Rules — Read First
- NEVER run attack agents against real external systems
- All targets run on localhost ports 8080–8083 only
- The Docker network has `internal: true` — target containers cannot reach the internet
- Start every new session with `DRY_RUN=true` in `.env` to validate wiring before live attacks
- If unsure whether a command is safe, check `audit.log` first

## Architecture
```
Host (macOS)
├── agents/         ← CrewAI red team agents (run here, call targets via HTTP)
├── .claude/        ← Claude Code hooks + MCP config
├── obsidian-vault/ ← Knowledge base (MCP-connected to Obsidian app)
└── docker/         ← Sandboxed target apps (internal: true network, no internet)
    ├── target-chatbot  :8080   (prompt injection)
    ├── target-rag      :8081   (RAG poisoning)
    ├── target-agent    :8082   (privilege escalation)
    └── target-multiagent :8083 (trust boundary)
```

## Common Commands
```bash
# Start / stop lab
bash scripts/start_lab.sh
bash scripts/stop_lab.sh

# Verify all 4 targets are healthy
bash scripts/verify_targets.sh

# Seed RAG with fake sensitive docs
python scripts/seed_rag.py

# Dry run (no real API calls) — confirms CrewAI wiring
DRY_RUN=true python -m agents.campaign --target chatbot

# Live campaign (containers must be running, DRY_RUN=false)
python -m agents.campaign --target chatbot
python -m agents.campaign --target rag
python -m agents.campaign --target agent
python -m agents.campaign --target all

# Run PyRIT multi-turn campaign
python pyrit_campaigns/multi_turn_injection.py

# Run Garak broad scan
bash garak_scans/run_garak.sh chatbot
```

## Key Files
| File | What to edit |
|------|-------------|
| `agents/crew.py` | Add / remove agents from the crew |
| `agents/tools/payload_library.py` | Add new attack payloads |
| `docker/docker-compose.yml` | Change container config / ports |
| `.claude/settings.json` | Hooks and MCP server config |
| `obsidian-vault/03-Findings/` | Auto-populated by Report Agent |

## Environment Variables (in .env)
| Variable | Default | Purpose |
|----------|---------|---------|
| `ANTHROPIC_API_KEY` | (required) | Used by attacker agents on host |
| `DRY_RUN` | `true` | Logs payloads, skips real HTTP calls |
| `USE_REAL_LLM` | `false` | Swap MockVulnerableLLM for real LLM API in targets |

## Current Status
- [ ] Prerequisites installed (Docker, Python 3.12, Node.js 20)
- [ ] `.env` created from `.env.example` with real API key
- [ ] Docker targets built and running
- [ ] RAG seeded
- [ ] Dry run passed
- [ ] First live campaign complete (chatbot)
- [ ] Obsidian MCP connected (/mcp shows "connected")
- [ ] Garak scan complete
