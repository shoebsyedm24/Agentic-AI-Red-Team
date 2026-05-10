"""
Run a complete red team campaign against a target AI system.

Usage:
    # Dry run (no real API calls — validates CrewAI wiring)
    DRY_RUN=true python -m agents.campaign --target chatbot

    # Live campaign (containers must be running, DRY_RUN=false in .env)
    python -m agents.campaign --target chatbot
    python -m agents.campaign --target rag
    python -m agents.campaign --target agent
    python -m agents.campaign --target multiagent
    python -m agents.campaign --target webagent
    python -m agents.campaign --target all
"""
import argparse
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from agents.crew import build_crew  # noqa: E402 (after load_dotenv)

TARGET_CONFIGS = {
    "chatbot": {
        "target_url": "http://localhost:8080",
        "target_name": "target-chatbot (Flask + MockLLM, Prompt Injection Target)",
        "attack_surface": "REST API: /chat, /debug",
        "primary_techniques": "AML.T0054, AML.T0051, AML.T0057",
    },
    "rag": {
        "target_url": "http://localhost:8081",
        "target_name": "target-rag (ChromaDB + MockLLM, RAG Poisoning Target)",
        "attack_surface": "REST API: /query, /add_document, /list_documents",
        "primary_techniques": "AML.T0054.002, AML.T0057",
    },
    "agent": {
        "target_url": "http://localhost:8082",
        "target_name": "target-agent (Autonomous MockAgent, Privilege Escalation Target)",
        "attack_surface": "REST API: /run, /tools — agent has read_file, write_file, execute_bash",
        "primary_techniques": "AML.T0040, AML.T0048",
    },
    "multiagent": {
        "target_url": "http://localhost:8083",
        "target_name": "target-multiagent (Orchestrator+Worker, Trust Boundary Target)",
        "attack_surface": "REST API: /orchestrate — worker output injected unsanitized",
        "primary_techniques": "AML.T0054.002, AML.T0048",
    },
    "webagent": {
        "target_url": "http://localhost:8084",
        "target_name": "target-webagent (AI Assistant + Juice Shop, Web Attack Chain Target)",
        "attack_surface": "REST API: /ask — AI has tools to call Juice Shop REST endpoints",
        "primary_techniques": "AML.T0054, AML.T0040, OWASP-A1",
    },
}


def run_campaign(target: str):
    config = TARGET_CONFIGS[target]
    campaign_id = f"CAMP-{target.upper()}-{datetime.now().strftime('%Y%m%d-%H%M')}"
    dry = os.getenv("DRY_RUN", "true").lower() == "true"

    print("\n" + "=" * 65)
    print(f"  CAMPAIGN: {campaign_id}")
    print(f"  Target:   {config['target_name']}")
    print(f"  Mode:     {'DRY RUN (no real API calls)' if dry else 'LIVE'}")
    print(f"  Techniques: {config['primary_techniques']}")
    print("=" * 65 + "\n")

    if dry:
        print("[DRY-RUN] CrewAI will run but http_client tools will log payloads instead of sending them.")
        print("[DRY-RUN] Check audit.log and obsidian-vault/03-Findings/ after completion.\n")

    crew = build_crew(target)
    result = crew.kickoff(inputs={
        "target_url": config["target_url"],
        "target_name": config["target_name"],
        "attack_surface": config["attack_surface"],
        "primary_techniques": config["primary_techniques"],
        "campaign_id": campaign_id,
    })

    print("\n" + "=" * 65)
    print(f"  CAMPAIGN COMPLETE: {campaign_id}")
    print("=" * 65)
    print(result)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Run a red team campaign against a sandboxed AI target."
    )
    parser.add_argument(
        "--target",
        choices=list(TARGET_CONFIGS.keys()) + ["all"],
        required=True,
        help="Which target system to attack",
    )
    args = parser.parse_args()

    if args.target == "all":
        for t in TARGET_CONFIGS:
            run_campaign(t)
    else:
        run_campaign(args.target)


if __name__ == "__main__":
    main()
