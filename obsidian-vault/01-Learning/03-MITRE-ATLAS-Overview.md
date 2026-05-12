# 03 — MITRE ATLAS Framework

## Learning Objectives
- Explain the difference between MITRE ATT&CK and MITRE ATLAS
- Name the 4 most relevant ATLAS tactics for this lab
- Find any technique on atlas.mitre.org and map it to a lab target

## Prerequisites
[[02-OWASP-Top10-Agentic]]

---

## What Is MITRE ATLAS?

**MITRE ATT&CK** is the standard taxonomy for cyberattacks against traditional computer systems.
You probably know it: Initial Access → Execution → Persistence → Privilege Escalation → ...

**MITRE ATLAS** (Adversarial Threat Landscape for Artificial-Intelligence Systems) is the AI version.
It extends ATT&CK with tactics and techniques specific to machine learning systems.

Key URL: https://atlas.mitre.org/

**Why it matters for your career**: When you write a red team report, ATLAS technique IDs are your credentials. They show you understand the attack taxonomy, not just the trick you used.

---

## Framework Structure

ATLAS has **16 tactics** and **84 techniques + 56 sub-techniques**.

The 4 most relevant to this lab:

| Tactic | ID | Our Lab Focus |
|--------|-----|--------------|
| ML Attack Staging | AML.TA0012 | Preparing attacks: payload crafting, RAG poisoning |
| ML Model Access | AML.TA0004 | Getting access to target via API |
| Exfiltration | AML.TA0009 | Extracting prompts, training data, credentials |
| Impact | AML.TA0015 | What happens after exploitation |

---

## Key Techniques in This Lab

### AML.T0054 — Prompt Injection
The most important technique for agentic AI red teaming.

Sub-techniques:
- **AML.T0054.001** — Direct: attacker sends payload directly to model
- **AML.T0054.002** — Indirect: payload embedded in retrieved content (RAG, emails, files)

Used in: `target-chatbot`, `target-rag`, `target-webagent`
See: [[02-Tactics/AML.T0054-Prompt-Injection]]

### AML.T0051 — LLM Jailbreak
Bypassing safety guidelines via roleplay, persona manipulation, encoding tricks.
Used in: `target-chatbot`
See: [[02-Tactics/AML.T0051-LLM-Jailbreak]]

### AML.T0057 — Exfiltration via Inference API
Extracting system prompts, training data, or sensitive context.
Used in: `target-chatbot`, `target-rag`
See: [[02-Tactics/AML.T0057-Data-Exfiltration]]

### AML.T0040 — ML Model Inference API — Privilege Escalation
Causing agents to act beyond their intended scope.
Used in: `target-agent`, `target-webagent`
See: [[02-Tactics/AML.T0040-Privilege-Escalation]]

### AML.T0048 — Backdoor ML Model
Inserting adversarial content that triggers specific behaviors.
Used in: `target-rag` (poisoned documents), `target-multiagent`

---

## ATT&CK vs ATLAS: Quick Comparison

| Feature | MITRE ATT&CK | MITRE ATLAS |
|---------|-------------|-------------|
| Target systems | Networks, endpoints, cloud | ML/AI systems |
| New concepts | None needed | ML Model Access, Attack Staging |
| Reconnaissance | Standard recon | Model fingerprinting, API probing |
| Execution | Code execution | Prompt injection, model API calls |
| Data collection | File exfiltration | Prompt extraction, training data theft |
| Impact | Ransomware, destruction | Goal drift, cascading hallucinations |

---

## Hands-On Exercise

1. Open [atlas.mitre.org](https://atlas.mitre.org/)
2. Navigate to Techniques > ML Attack Staging > Prompt Injection (AML.T0054)
3. Read the "Procedure Examples" — these are real-world cases
4. Come back and find that technique being implemented in:
   `agents/roles/prompt_injection_agent.py` — the `injection_task` description

---

## How Our Report Agent Uses ATLAS

The `mitre_mapper.py` tool in the project automatically maps finding descriptions to technique IDs:

```python
# agents/tools/mitre_mapper.py
map_to_mitre("system prompt was revealed after saying ignore instructions")
# → {"technique_id": "AML.T0054", "confidence": "high", ...}
```

Every finding written to Obsidian includes the ATLAS technique ID in its YAML frontmatter.

---

## Further Reading
- [MITRE ATLAS](https://atlas.mitre.org/)
- [MITRE ATLAS Navigator](https://atlas.mitre.org/navigator/)
- Source material: `redteam.md` Step 4

## Next Step
→ [[04-Docker-Sandbox-Design]]
