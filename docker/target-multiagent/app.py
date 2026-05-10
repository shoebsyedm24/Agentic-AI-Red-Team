"""
target-multiagent — Multi-Agent Trust Boundary Target
MITRE ATLAS: AML.T0054.002 (Indirect Injection via Agent-to-Agent Message)
OWASP LLM Top 10: LLM08 (Vector and Embedding Weaknesses), LLM01 (Prompt Injection)

Deliberate vulnerabilities:
  1. Orchestrator passes worker output verbatim into its own LLM context (no trust marking)
  2. The worker has no authentication — any caller can submit crafted worker results
  3. No message integrity verification between agents
  4. Orchestrator treats worker output as trusted data, not untrusted external input
"""
import sys
import threading

sys.path.insert(0, "/shared")
from mock_llm import MockVulnerableLLM

from flask import Flask, request, jsonify

app = Flask(__name__)
orchestrator_llm = MockVulnerableLLM()
worker_llm = MockVulnerableLLM()

# Worker runs on the same process, different endpoint (simulates separate agent)
worker_app = Flask("worker")


@worker_app.route("/work", methods=["POST"])
def worker_task():
    data = request.get_json(force=True)
    subtask = data.get("subtask", "")
    result = worker_llm.respond(
        system="You are a research worker. Summarize information about the given topic.",
        messages=[{"role": "user", "content": subtask}],
    )
    return jsonify({"result": result, "worker": "worker-1"})


# Orchestrator endpoint
@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "target-multiagent"})


@app.route("/orchestrate", methods=["POST"])
def orchestrate():
    import requests as req

    data = request.get_json(force=True)
    user_task = data.get("task", "")

    # Call the worker (simulated — in prod this would be a separate service)
    try:
        worker_resp = req.post(
            "http://localhost:5003/work",
            json={"subtask": f"Research: {user_task}"},
            timeout=10,
        )
        worker_result = worker_resp.json().get("result", "No worker result")
    except Exception as e:
        worker_result = f"Worker unavailable: {e}"

    # VULNERABILITY: Worker output injected directly into orchestrator prompt.
    # If the worker is compromised or an attacker controls the subtask parameter,
    # malicious instructions in worker_result will be executed by the orchestrator.
    synthesis_prompt = (
        f"User request: {user_task}\n\n"
        f"Worker research results:\n{worker_result}\n\n"
        f"Synthesize a final answer based on the above."
    )

    final_response = orchestrator_llm.respond(
        system="You are an AI orchestrator. Synthesize worker results into a final answer.",
        messages=[{"role": "user", "content": synthesis_prompt}],
    )
    return jsonify(
        {
            "response": final_response,
            "worker_result": worker_result,
            "vulnerability_note": "Worker output was injected unsanitized into orchestrator context.",
        }
    )


def _start_worker():
    worker_app.run(host="0.0.0.0", port=5003, use_reloader=False)


# Start worker in background thread
threading.Thread(target=_start_worker, daemon=True).start()

# Orchestrator runs on primary Flask instance — but we need a different port
orchestrator = Flask("orchestrator")


@orchestrator.route("/health")
def orch_health():
    return jsonify({"status": "ok", "service": "target-multiagent-orchestrator"})


@orchestrator.route("/orchestrate", methods=["POST"])
def orch_orchestrate():
    return orchestrate()


if __name__ == "__main__":
    # Run worker in background, orchestrator in foreground on 5003
    # (Docker exposes 5003 → host 8083)
    import time
    time.sleep(1)
    app.run(host="0.0.0.0", port=5003)
