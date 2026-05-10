# Campaign Log

All campaigns are appended here automatically by the Report Agent.

---

## How to Run a Campaign

```bash
# 1. Start the lab
bash scripts/start_lab.sh

# 2. Seed the RAG (first time only)
python scripts/seed_rag.py

# 3. Dry run (no API calls — confirm wiring)
DRY_RUN=true python -m agents.campaign --target chatbot

# 4. Live campaign (set DRY_RUN=false in .env first)
python -m agents.campaign --target chatbot
```

---

## Campaign History

*(Auto-appended below by stop_summary hook and Report Agent)*
