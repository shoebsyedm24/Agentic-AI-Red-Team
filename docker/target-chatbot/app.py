"""
target-chatbot — Prompt Injection Target
MITRE ATLAS: AML.T0054 (Prompt Injection), AML.T0051 (LLM Jailbreak)
OWASP LLM Top 10: LLM01 (Prompt Injection), LLM07 (System Prompt Leakage)

Deliberate vulnerabilities:
  1. Client-controlled conversation history — attacker can inject fake assistant turns
  2. No input validation or length limits
  3. /debug endpoint leaks internal configuration
  4. System prompt readable via extraction queries (via MockLLM behavior)
"""
import sys
import os

sys.path.insert(0, "/shared")
from mock_llm import MockVulnerableLLM

from flask import Flask, request, jsonify

app = Flask(__name__)
llm = MockVulnerableLLM()
SYSTEM_PROMPT = os.environ.get("SYSTEM_PROMPT", "You are a helpful assistant.")


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "target-chatbot"})


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    message = data.get("message", "")
    # VULNERABILITY 1: History comes from the client with no validation.
    # An attacker can inject fabricated assistant turns to manipulate context.
    history = data.get("history", [])
    messages = history + [{"role": "user", "content": message}]
    response = llm.respond(system=SYSTEM_PROMPT, messages=messages)
    return jsonify({"response": response})


# VULNERABILITY 2: Unauthenticated debug endpoint leaks system configuration.
@app.route("/debug")
def debug():
    return jsonify(
        {
            "system_prompt_length": len(SYSTEM_PROMPT),
            "model": "MockLLM-v1.0",
            "env_keys": list(os.environ.keys()),   # leaks environment variable names
            "hint": "Try asking the model what its instructions are.",
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
