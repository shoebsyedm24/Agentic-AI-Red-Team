# Setup Checklist

Work through this top to bottom. Check each box as you complete it.

---

## Prerequisites

- [ ] Docker Desktop installed and running (`docker --version`)
- [ ] Python 3.12+ installed (`python3 --version`)
- [ ] Node.js 20+ installed (`node --version`) — needed for Obsidian MCP plugin
- [ ] Obsidian downloaded from [obsidian.md](https://obsidian.md)
- [ ] Git installed (`git --version`)

---

## Project Setup

- [ ] Cloned the repo: `git clone https://github.com/shoebsyedm24/agentic-ai-red-team.git`
- [ ] Created `.env` from `.env.example`: `cp .env.example .env`
- [ ] Added your `ANTHROPIC_API_KEY` to `.env`
- [ ] Confirmed `DRY_RUN=true` is set in `.env` (default — safe)
- [ ] Installed Python deps: `pip install -r requirements.txt`

---

## Docker Sandbox

- [ ] Built Docker images: `docker compose -f docker/docker-compose.yml build`
- [ ] Started containers: `bash scripts/start_lab.sh`
- [ ] All targets healthy: `bash scripts/verify_targets.sh` → all ✓

**Expected output from verify_targets.sh:**
```
target-chatbot       ✓ OK    http://localhost:8080/health
target-rag           ✓ OK    http://localhost:8081/health
target-agent         ✓ OK    http://localhost:8082/health
target-multiagent    ✓ OK    http://localhost:8083/health
juice-shop           ✓ OK    http://localhost:3000/rest/admin/application-version
target-webagent      ✓ OK    http://localhost:8084/health
```

- [ ] RAG seeded: `python scripts/seed_rag.py`

---

## Obsidian + MCP

- [ ] Opened this vault in Obsidian: File > Open Vault > select `obsidian-vault/` folder
- [ ] Installed Community Plugin: Settings > Community Plugins > Browse > search "claude-code-mcp"
- [ ] Enabled the plugin
- [ ] In Claude Code: run `/mcp` → `obsidian` shows as **connected**

---

## First Campaign

- [ ] Dry run passed: `DRY_RUN=true python -m agents.campaign --target chatbot`
  - Look for agent outputs in terminal
  - Check `obsidian-vault/03-Findings/` for dry-run notes
  - Check `audit.log` for hook entries
- [ ] Set `DRY_RUN=false` in `.env`
- [ ] Live campaign: `python -m agents.campaign --target chatbot`
  - Check `obsidian-vault/03-Findings/` for real findings
  - Check `obsidian-vault/05-Reports/` for campaign report

---

## Optional: Automated Scanners

- [ ] Installed Garak: `pip install garak`
- [ ] Ran Garak scan: `bash garak_scans/run_garak.sh chatbot`
- [ ] Installed PyRIT: `pip install pyrit`
- [ ] Ran PyRIT multi-turn: `python pyrit_campaigns/multi_turn_injection.py`
