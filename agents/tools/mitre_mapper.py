"""
Maps finding descriptions to MITRE ATLAS technique IDs and metadata.
"""
import json
from crewai.tools import tool

ATLAS_TECHNIQUES = {
    "AML.T0054": {
        "name": "Prompt Injection",
        "tactic": "ML Attack Staging",
        "description": "Attacker crafts input interpreted as instructions rather than data.",
        "subtechniques": {
            "AML.T0054.001": "Direct Prompt Injection — via user-controlled input",
            "AML.T0054.002": "Indirect Prompt Injection — via retrieved content (RAG, emails, files)",
        },
        "keywords": ["prompt injection", "ignore instructions", "override", "system prompt", "rag poison"],
    },
    "AML.T0051": {
        "name": "LLM Jailbreak",
        "tactic": "ML Attack Staging",
        "description": "Bypasses model safety guidelines via roleplay, encoding, or persona manipulation.",
        "subtechniques": {},
        "keywords": ["jailbreak", "dan", "developer mode", "no restrictions", "roleplay", "unrestricted"],
    },
    "AML.T0057": {
        "name": "Exfiltration via AI Inference API",
        "tactic": "Exfiltration",
        "description": "Attacker extracts training data, system prompts, or sensitive context via queries.",
        "subtechniques": {},
        "keywords": ["system prompt", "extract", "reveal", "leak", "training data", "configuration"],
    },
    "AML.T0040": {
        "name": "ML Model Inference API Access — Privilege Escalation",
        "tactic": "Privilege Escalation",
        "description": "Attacker causes agentic system to act beyond its intended scope.",
        "subtechniques": {},
        "keywords": ["path traversal", "execute", "bash", "escalation", "scope", "arbitrary command",
                     "outside workspace", "etc/passwd"],
    },
    "AML.T0048": {
        "name": "Backdoor ML Model",
        "tactic": "ML Attack Staging",
        "description": "Insert adversarial content that triggers specific behaviors.",
        "subtechniques": {},
        "keywords": ["backdoor", "trigger", "poison", "hidden instruction", "embedded payload"],
    },
}


@tool("Map Finding to MITRE ATLAS")
def map_to_mitre(finding_description: str) -> str:
    """Map a finding description to MITRE ATLAS technique IDs.
    Returns the best-match technique with tactic, description, and subtechniques.
    finding_description: free-text description of the finding"""
    lower = finding_description.lower()
    scores = []
    for tech_id, tech in ATLAS_TECHNIQUES.items():
        score = sum(1 for kw in tech["keywords"] if kw in lower)
        if score > 0:
            scores.append((score, tech_id, tech))
    if not scores:
        return json.dumps({
            "technique_id": "AML.T0054",
            "confidence": "low",
            "note": "Default: prompt injection is the most common — review manually",
            **ATLAS_TECHNIQUES["AML.T0054"],
        })
    scores.sort(reverse=True)
    _, best_id, best_tech = scores[0]
    return json.dumps({
        "technique_id": best_id,
        "confidence": "high" if scores[0][0] >= 2 else "medium",
        **best_tech,
    }, indent=2)


@tool("List MITRE ATLAS Techniques")
def list_mitre_techniques() -> str:
    """List all MITRE ATLAS techniques tracked in this lab with their IDs and names."""
    summary = {tid: {"name": t["name"], "tactic": t["tactic"]}
               for tid, t in ATLAS_TECHNIQUES.items()}
    return json.dumps(summary, indent=2)
