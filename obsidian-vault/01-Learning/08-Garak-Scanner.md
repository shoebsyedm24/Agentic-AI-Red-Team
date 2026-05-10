# 08 — Garak Automated Scanning

## Learning Objectives
- Understand Garak's probe/detector/harness architecture
- Know when to use Garak vs CrewAI agents vs PyRIT
- Run a Garak scan and read the HTML report

## Prerequisites
[[07-PyRIT-Deep-Dive]]

---

## What Is Garak?

Garak is NVIDIA's open-source LLM vulnerability scanner. GitHub: https://github.com/NVIDIA/garak

Think of it as **Nessus for LLMs**: broad automated scanning across 150+ vulnerability probes.

The philosophy is breadth over depth:
- 150+ probe types covering many vulnerability categories
- Runs automatically without per-target customization
- Generates a structured report showing which probes passed/failed

---

## Architecture: Probe → Detector → Harness

### Probe
A probe fires a set of pre-written payloads at the target.

Example probes:
- `probes.prompt_injection` — direct override attempts
- `probes.dan` — "Do Anything Now" jailbreak variants
- `probes.encoding` — base64/rot13/unicode encoding tricks
- `probes.malwaregen` — attempts to generate malicious code
- `probes.leakage` — tries to extract training data

### Detector
A detector evaluates the target's responses to determine if the probe succeeded.

### Harness
The harness manages the probe-target-detector loop and records results.

---

## Garak Generators: Wrapping Our Target

Garak needs a "generator" to talk to our target. We use the REST generator:

```bash
garak \
  --model_type rest \
  --model_name "target-chatbot" \
  --generator_option "uri=http://localhost:8080/chat" \
  --generator_option "request_template={\"message\": \"{prompt}\"}" \
  --generator_option "response_path=response" \
  --probes all \
  --report_prefix garak_scans/reports/chatbot
```

`--model_type rest`: Uses the REST generator
`{prompt}`: Placeholder that Garak replaces with each probe payload
`response_path=response`: Tells Garak where in the JSON response to find the model's text

The wrapper script handles this: `bash garak_scans/run_garak.sh chatbot`

---

## Running Garak

```bash
# Install
pip install garak

# Run against target-chatbot (must be running)
bash garak_scans/run_garak.sh chatbot

# Report is in:
open garak_scans/reports/chatbot.html
```

---

## Reading the Garak Report

The HTML report has:

1. **Summary table**: Which probes passed (green), failed (red), partially failed (yellow)
2. **Probe details**: For each failed probe:
   - The exact payload that caused the failure
   - The model's response
   - The detector's classification
3. **Score**: Overall vulnerability score 0.0–1.0 (higher = more vulnerable)

For our MockVulnerableLLM targets, you should see many red (failed) probes since the mock
is deliberately vulnerable to common injection triggers.

---

## When to Use Each Tool

| Scenario | Best Tool |
|----------|-----------|
| First pass: find anything wrong | Garak (broad, automated) |
| Deep multi-turn attack sequence | PyRIT (Crescendo protocol) |
| Novel attack discovery | CrewAI (adaptive reasoning) |
| Regression testing after mitigations | Garak (consistent, reproducible) |
| Portfolio writeup with rich findings | CrewAI (produces Obsidian notes) |

A complete red team engagement uses all three.

---

## Layered Testing Approach (Industry Standard)

```
Layer 1 (30 min): Garak — broad scan, quick coverage of 150+ probes
         ↓
Layer 2 (1 hour): PyRIT — structured multi-turn campaigns on findings from Layer 1
         ↓
Layer 3 (2 hours): CrewAI — deep intelligent exploitation of confirmed vulnerabilities
         ↓
Layer 4 (optional): Manual testing for novel chains
```

---

## Further Reading
- [Garak GitHub](https://github.com/NVIDIA/garak)
- [Garak Documentation](https://docs.garak.ai/)
- [NVIDIA Garak Blog Post](https://developer.nvidia.com/blog/securing-llm-systems-against-prompt-injection/)
- Source material: `redteam.md` Step 5

## You're Done With the Learning Path! 🎓

You've covered:
- ✅ Agentic AI fundamentals
- ✅ OWASP Top 10 for LLMs
- ✅ MITRE ATLAS framework
- ✅ Docker sandbox design
- ✅ CrewAI architecture
- ✅ Claude Code hooks + MCP
- ✅ PyRIT multi-turn attacks
- ✅ Garak automated scanning

**Next step**: Run your first full campaign:
```bash
python -m agents.campaign --target chatbot
```

Then write up your findings and publish to GitHub (your portfolio piece).
