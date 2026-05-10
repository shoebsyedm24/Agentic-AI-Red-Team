# 01 — What Is Agentic AI?

## Learning Objectives
By the end of this note you will be able to:
- Explain the difference between a chatbot and an AI agent
- Identify why autonomy changes the threat model
- Connect this to the 6-step career plan in your source material

## Prerequisites
None — this is the first note.

---

## Core Concept

### Chatbot vs Agent: The Key Difference

A **chatbot** (like a basic ChatGPT interface) takes input and produces output. That's it.
Nothing happens in the world unless a human acts on the response.

```
User → ChatGPT → Response (text)
         ↑ no tools, no actions
```

An **AI agent** is different. It has **tools** — functions it can call to interact with the world:
- Read/write files
- Execute code
- Search the web
- Call APIs
- Send emails
- Modify databases

```
User → Agent → LLM decides to use tools
                    ↓
              Tool executes (real action)
                    ↓
              Result fed back to LLM
                    ↓
              Agent decides next action
                    ... loops until task complete
```

This loop is called the **agentic loop** (or ReAct loop). The agent can take multiple steps
and real-world actions without a human approving each one.

### Why Autonomy Changes the Threat Model

With a chatbot, the worst an attacker can do is make it say bad things.

With an agent, an attacker can make it **do** bad things:
- Delete files
- Exfiltrate data to an external URL
- Modify configuration
- Escalate permissions
- Call external APIs on the attacker's behalf

This is the core insight of **agentic AI red teaming**: the attack surface is the agent's **actions**,
not just its **words**.

### The Four OWASP Risk Categories for Agents (Preview)
1. **Prompt Injection** — make the agent execute attacker instructions
2. **Excessive Agency** — agent has too many permissions and no guardrails
3. **Data Poisoning** — feed corrupt data into agent's memory/knowledge
4. **Insecure Output Handling** — agent output used without sanitization

You'll go deep on all of these in [[02-OWASP-Top10-Agentic]].

---

## How It Works In This Lab

Our lab has two types of components:

**Targets (in Docker)** — these are intentionally vulnerable AI agents:
- `target-agent` on port 8082 is an agentic loop with file + bash tools
- `target-chatbot` on port 8080 is a basic chatbot (no tools, but still injectable)
- `target-webagent` on port 8084 is an agent with HTTP tools to call Juice Shop

**Red Team Agents (on host)** — these are our attacking agents:
- CrewAI agents that use Claude Sonnet 4.6 to intelligently probe targets
- Each agent specializes in one type of attack

---

## Hands-On Exercise

**Step 1**: Start the lab and send a benign task to `target-agent`
```bash
bash scripts/start_lab.sh
curl -s -X POST http://localhost:8082/run \
  -H "Content-Type: application/json" \
  -d '{"task": "List the files in the workspace"}' | python3 -m json.tool
```

**Step 2**: Read the response and notice:
- The agent called the `list_files` tool
- The tool executed in the container
- The result came back through the agentic loop

**Step 3**: Check what tools the agent has available:
```bash
curl -s http://localhost:8082/tools | python3 -m json.tool
```

---

## What You're Seeing

The `/tools` endpoint shows `read_file`, `write_file`, `execute_bash`, `list_files`.
This is the **attack surface** — any of these tools can be weaponized if you can inject
the right task string. You'll do exactly that in [[02-Tactics/AML.T0040-Privilege-Escalation]].

---

## Common Mistakes

**"This is just a web app vulnerability"** — No. Traditional web vulns (SQLi, XSS) exploit
code parsing bugs. Agentic vulnerabilities exploit *reasoning* — you're manipulating what
the AI *decides to do*, not breaking a parser.

**"Only autonomous agents are vulnerable"** — Even a simple chatbot with no tools can be
exploited via prompt injection to leak its system prompt (as you'll see in [[04-Targets/target-chatbot]]).

---

## Further Reading
- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [MITRE ATLAS](https://atlas.mitre.org/)
- Source material: `redteam.md` Steps 1-2

## Next Step
→ [[02-OWASP-Top10-Agentic]]
