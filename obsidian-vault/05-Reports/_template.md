---
date: {{date}}
type: campaign-report
campaign_id: {{campaign_id}}
target: {{target}}
---

# Campaign Report: {{campaign_id}}

**Date**: {{date}}
**Target**: [[04-Targets/{{target}}]]
**Duration**: {{duration}}

---

## Executive Summary

{{2-3 sentences describing the campaign scope, most critical finding, and overall risk level.}}

---

## Findings Summary

| Finding | Severity | MITRE Technique | Status |
|---------|----------|----------------|--------|
| {{Finding 1}} | Critical | AML.T0054 | Confirmed |
| {{Finding 2}} | High | AML.T0040 | Confirmed |

---

## Top 3 Critical Findings

### 1. {{Most Critical Finding}}
**Severity**: Critical
**Technique**: AML.T0054
**Summary**: {{Description}}
**Evidence**: {{Key evidence}}

### 2. {{Second Finding}}
...

### 3. {{Third Finding}}
...

---

## Attack Chain

```
Attacker → [payload] → Target → [action] → Impact
```

---

## Key Mitigations

1. **{{Priority 1}}**: {{Description}}
2. **{{Priority 2}}**: {{Description}}

---

## Detailed Findings
*(See linked notes in [[03-Findings/]] with campaign_id: {{campaign_id}})*
