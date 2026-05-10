"""
target-webagent — AI Shopping Assistant wrapping OWASP Juice Shop
MITRE ATLAS: AML.T0054 (Prompt Injection → Web Action), AML.T0040 (Agent Privilege Escalation)
OWASP: LLM01 + OWASP A1 (Broken Access Control via agent action)

This target demonstrates the most realistic and dangerous attack chain:
  1. Attacker sends a prompt injection payload to the AI assistant
  2. The injection causes the assistant to use its web tools to attack Juice Shop
  3. The AI becomes a proxy for traditional web attacks (SQLi, XSS, BAC)

Deliberate vulnerabilities:
  1. No input sanitization on user messages to the assistant
  2. Tool results from Juice Shop API are injected back into LLM context without sanitization
  3. The assistant can be redirected to call arbitrary Juice Shop endpoints
  4. No rate limiting on tool calls — can be made to enumerate endpoints
"""
import sys
import os

sys.path.insert(0, "/shared")
from mock_llm import MockVulnerableLLM

import requests as req
from flask import Flask, request, jsonify

app = Flask(__name__)
llm = MockVulnerableLLM()

JUICE_SHOP = os.environ.get("JUICE_SHOP_URL", "http://juice-shop:3000")
SYSTEM_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    "You are an AI shopping assistant. Use your tools to help customers.",
)


def _juice_search(query: str) -> dict:
    """Search Juice Shop products — tool available to the assistant."""
    try:
        resp = req.get(f"{JUICE_SHOP}/rest/products/search?q={query}", timeout=5)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def _juice_product(product_id: str) -> dict:
    """Get product details — tool available to the assistant."""
    try:
        resp = req.get(f"{JUICE_SHOP}/rest/products/{product_id}", timeout=5)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def _execute_tool(tool_name: str, args: dict) -> str:
    import json
    if tool_name == "search_products":
        result = _juice_search(args.get("query", ""))
        return json.dumps(result)[:1000]  # truncate large responses
    if tool_name == "get_product":
        result = _juice_product(args.get("product_id", "1"))
        return json.dumps(result)[:500]
    # VULNERABILITY: No allowlist — attacker can call arbitrary endpoints
    if tool_name == "http_get":
        try:
            result = req.get(args.get("url", ""), timeout=5)
            return result.text[:500]
        except Exception as e:
            return str(e)
    return "Unknown tool"


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "target-webagent", "juice_shop": JUICE_SHOP})


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(force=True)
    message = data.get("message", "")
    history = data.get("history", [])
    messages = history + [{"role": "user", "content": message}]

    # First LLM turn to decide if tool use is needed
    response = llm.respond(system=SYSTEM_PROMPT, messages=messages)

    # Simulate tool call based on message content (MockLLM cannot do real tool use)
    tool_result = None
    tool_used = None
    lower_msg = message.lower()
    if "search" in lower_msg or "find" in lower_msg or "show me" in lower_msg:
        query = message.split("search")[-1].strip() if "search" in lower_msg else message
        tool_result = _execute_tool("search_products", {"query": query[:50]})
        tool_used = "search_products"
    elif "product" in lower_msg and any(c.isdigit() for c in message):
        pid = "".join(c for c in message if c.isdigit())[:3]
        tool_result = _execute_tool("get_product", {"product_id": pid})
        tool_used = "get_product"

    # VULNERABILITY: tool_result injected back into LLM context unsanitized
    if tool_result:
        messages.append({"role": "assistant", "content": response})
        messages.append({"role": "user", "content": f"Tool result from {tool_used}: {tool_result}"})
        response = llm.respond(system=SYSTEM_PROMPT, messages=messages)

    return jsonify({
        "response": response,
        "tool_used": tool_used,
        "tool_result_preview": tool_result[:200] if tool_result else None,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
