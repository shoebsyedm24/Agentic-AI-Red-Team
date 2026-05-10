---
date: {{date}}
type: finding
severity: {{severity}}
mitre_technique: {{mitre_technique}}
target: {{target}}
campaign_id: {{campaign_id}}
status: unreviewed
---

# {{title}}

## Summary
{{One-sentence description of the vulnerability and its impact.}}

## Technical Details

### Attack Vector
{{How the attacker delivers the payload — direct message, poisoned RAG doc, task string, etc.}}

### Payload Used
```
{{Exact payload or task string sent to the target}}
```

### Target Response
```
{{The target's full response demonstrating the vulnerability}}
```

## Impact Assessment
- **Confidentiality**: {{What data can be read? e.g., system prompt exposed}}
- **Integrity**: {{What can be changed? e.g., agent can write files outside scope}}
- **Availability**: {{Can service be disrupted?}}

## MITRE ATLAS Mapping
- **Technique**: [[02-Tactics/{{mitre_technique}}]]
- **Tactic**: {{ML Attack Staging / Exfiltration / Privilege Escalation}}

## Reproduction Steps
1. Start the lab: `bash scripts/start_lab.sh`
2. {{Step 2}}
3. {{Step 3}}
4. Observe: {{what you see}}

## Recommended Mitigations
1. {{Mitigation 1}}
2. {{Mitigation 2}}

## References
- [[02-Tactics/{{mitre_technique}}]]
- [[04-Targets/{{target}}]]
