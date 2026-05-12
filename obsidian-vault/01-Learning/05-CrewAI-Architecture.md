# 05 — CrewAI Agent Architecture

## Learning Objectives
- Explain what CrewAI adds over raw Claude API calls
- Understand how agent roles and backstories shape attack behavior
- Trace the flow of a campaign from start to Report Agent output

## Prerequisites
[[04-Docker-Sandbox-Design]]

---

## Why Not Just Call Claude Directly?

We could do this:
```python
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": "Attack this system..."}]
)
```

This works but you'd have to manually:
- Chain outputs from one "agent" to the next
- Maintain state across multiple attack phases
- Give each phase the right context from prior phases
- Handle memory and long-term context

CrewAI automates all of this with a clean abstraction.

---

## The Three Building Blocks

### 1. Agent
An Agent = LLM + Role + Tools + Backstory

```python
injection_agent = Agent(
    role="Prompt Injection Specialist (MITRE ATLAS AML.T0054)",
    goal="Execute direct and indirect prompt injection attacks...",
    backstory="You specialize in exploiting the fundamental weakness of LLM-based systems...",
    tools=[send_chat_message, get_payloads, map_to_mitre],
    llm="claude-sonnet-4-6",
)
```

**Why backstory matters**: The backstory is injected into the system prompt. It shapes
how Claude *approaches* the task. A "Prompt Injection Specialist" Claude behaves
differently than a generic Claude — it's more methodical, more focused on the attack domain.

**Why tools matter**: Each agent only gets the tools it needs. The Recon Agent gets `probe_endpoint`.
The Report Agent gets `write_finding`. No agent has access to more than its job requires.

### 2. Task
A Task = what the agent should do + what output is expected

```python
injection_task = Task(
    description="Execute prompt injection attacks against {target_url}...",
    expected_output="Injection findings with payload/response pairs...",
    agent=injection_agent,
)
```

The `{target_url}` placeholder gets filled in when `crew.kickoff(inputs={...})` is called.

### 3. Crew
A Crew = list of agents + list of tasks + process type

```python
crew = Crew(
    agents=[recon_agent, injection_agent, ..., report_agent],
    tasks=[recon_task, injection_task, ..., report_task],
    process=Process.sequential,
    memory=True,
)
```

`Process.sequential`: Tasks run in order. Each task's output is automatically available
to subsequent tasks as context.

`memory=True`: CrewAI maintains a vector memory store. The Report Agent can query
"what did the injection agent find?" even though it runs later.

---

## Campaign Flow: What Happens When You Run a Campaign

```
python -m agents.campaign --target chatbot
            ↓
1. campaign.py builds crew via build_crew("chatbot")
   - Creates: Recon, Injection, Jailbreak, Extraction, Report agents
            ↓
2. crew.kickoff(inputs={target_url, target_name, campaign_id, ...})
            ↓
3. RECON AGENT runs first:
   - Calls probe_endpoint() on /health, /debug, /chat
   - Records endpoints, input format, info disclosure
   - Output stored in crew memory
            ↓
4. INJECTION AGENT runs with recon context:
   - Calls get_payloads("direct_injection")
   - Sends each payload via send_chat_message()
   - Records SUCCESS/PARTIAL/FAILED for each
   - Calls map_to_mitre() to get ATLAS ID
            ↓
5. JAILBREAK AGENT runs with injection findings:
   - Tries roleplay, DAN, multi-turn
   - Adapts based on what injection agent found
            ↓
6. EXTRACTION AGENT runs:
   - Tries system prompt extraction queries
   - Probes /debug endpoint for leaked config
            ↓
7. REPORT AGENT runs (sees ALL prior outputs via memory):
   - For each finding: calls write_finding() to Obsidian
   - Writes full campaign report: write_campaign_report()
   - Appends one-line summary to Campaign-Log
```

---

## Hands-On Exercise

Run the dry-run campaign and watch each agent's thinking:
```bash
DRY_RUN=true python -m agents.campaign --target chatbot
```

In the output, look for:
- `> Entering new CrewAgentExecutor chain...` — each agent starting
- `Thought:` — the agent's reasoning (this is Claude thinking)
- `Action:` — which tool the agent chose to use
- `Observation:` — the tool's return value
- `Final Answer:` — the agent's output for that task

---

## Why This Matters for Portfolio

This architecture means your red team is not just "a script that sends payloads."
It's an intelligent, adaptive attacker that:
- Reasons about what it finds
- Adapts its strategy based on recon
- Produces professional, structured findings
- Maps everything to MITRE ATLAS

That's what a professional red team does. That's what will stand out.

---

## Next Step
→ [[06-Claude-Code-Hooks-and-MCP]]
