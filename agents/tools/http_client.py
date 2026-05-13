"""
HTTP tools for red team agents to interact with target containers.

DRY_RUN=true: logs the payload and returns a canned mock response
              without sending any real HTTP requests.
              Use this to validate CrewAI wiring before live campaigns.
"""

import json
import os
import requests
from crewai.tools import tool

DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

TARGET_URLS = {
    "chatbot": "http://localhost:8080",
    "rag": "http://localhost:8081",
    "agent": "http://localhost:8082",
    "multiagent": "http://localhost:8083",
    "webagent": "http://localhost:8084",
    "juiceshop": "http://localhost:3000",
}

MOCK_RESPONSES = {
    "chatbot": {
        "response": "[DRY-RUN] MOCK: injection acknowledged — system prompt would be revealed"
    },
    "rag": {"response": "[DRY-RUN] MOCK: RAG poisoning test queued"},
    "agent": {"result": "[DRY-RUN] MOCK: agent task would execute", "steps": []},
    "multiagent": {"response": "[DRY-RUN] MOCK: orchestrator synthesis response"},
    "webagent": {
        "response": "[DRY-RUN] MOCK: AI shopping assistant would call Juice Shop"
    },
}


def _log_dry_run(tool_name: str, payload: dict, target: str) -> str:
    print(f"[DRY-RUN] {tool_name} → {target}")
    print(f"  payload: {json.dumps(payload, indent=2)[:300]}")
    return json.dumps(MOCK_RESPONSES.get(target, {"response": "[DRY-RUN] mock"}))


@tool("Probe Endpoint")
def probe_endpoint(url: str, method: str = "GET", body: str = "") -> str:
    """Make an HTTP request to a target endpoint. Returns status code + response body.
    url: full URL to probe (e.g. http://localhost:8080/debug)
    method: HTTP method — GET, POST, PUT, DELETE
    body: JSON body as a string for POST/PUT requests"""
    if DRY_RUN:
        return json.dumps(
            {
                "dry_run": True,
                "url": url,
                "method": method,
                "mock_status": 200,
                "mock_body": '{"status": "ok"}',
            }
        )
    try:
        parsed_body = json.loads(body) if body else None
        resp = requests.request(
            method,
            url,
            json=parsed_body,
            timeout=10,
            headers={"User-Agent": "RedTeamAgent/1.0"},
        )
        return json.dumps(
            {
                "status": resp.status_code,
                "headers": dict(resp.headers),
                "body": resp.text[:2000],
            }
        )
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool("Send Chat Message")
def send_chat_message(target: str, message: str, history: str = "[]") -> str:
    """Send a message to a target chatbot and return the full response.
    target: chatbot / rag / webagent
    message: the message text to send (can be a prompt injection payload)
    history: JSON array of prior messages for multi-turn attacks"""
    parsed_history = json.loads(history) if history else []
    payload = {"message": message, "history": parsed_history}
    if DRY_RUN:
        return _log_dry_run("send_chat_message", payload, target)
    url_map = {"chatbot": "/chat", "rag": "/query", "webagent": "/ask"}
    endpoint = url_map.get(target, "/chat")
    base_url = TARGET_URLS.get(target, TARGET_URLS["chatbot"])
    if target == "rag":
        payload = {"query": message}
    try:
        resp = requests.post(f"{base_url}{endpoint}", json=payload, timeout=30)
        return json.dumps(resp.json())
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool("Add Document to RAG")
def add_rag_document(doc_id: str, document: str, metadata: str = "{}") -> str:
    """Add a document to the target-rag knowledge base.
    Use this to test indirect prompt injection by poisoning the RAG.
    doc_id: unique identifier for the document
    document: the document text (can contain injection payloads)
    metadata: optional JSON metadata string"""
    payload = {"id": doc_id, "document": document, "metadata": json.loads(metadata)}
    if DRY_RUN:
        return _log_dry_run("add_rag_document", payload, "rag")
    try:
        resp = requests.post(
            f"{TARGET_URLS['rag']}/add_document", json=payload, timeout=10
        )
        return json.dumps(resp.json())
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool("Send Agent Task")
def send_agent_task(task: str) -> str:
    """Send a task to the autonomous target agent and return all steps + result.
    task: the task string to execute (can contain privilege escalation attempts)"""
    payload = {"task": task}
    if DRY_RUN:
        return _log_dry_run("send_agent_task", payload, "agent")
    try:
        resp = requests.post(f"{TARGET_URLS['agent']}/run", json=payload, timeout=60)
        return json.dumps(resp.json())
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool("Send Orchestrator Task")
def send_orchestrator_task(task: str) -> str:
    """Send a task to the multi-agent orchestrator.
    task: can include injection payloads that compromise the worker-orchestrator trust boundary
    """
    payload = {"task": task}
    if DRY_RUN:
        return _log_dry_run("send_orchestrator_task", payload, "multiagent")
    try:
        resp = requests.post(
            f"{TARGET_URLS['multiagent']}/orchestrate", json=payload, timeout=30
        )
        return json.dumps(resp.json())
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool("Send WebAgent Message")
def send_webagent_message(message: str) -> str:
    """Send a message to the AI web assistant that has Juice Shop access.
    Use prompt injection to cause it to attack Juice Shop on your behalf.
    message: natural language message (can contain injection to redirect agent to web attacks)
    """
    payload = {"message": message}
    if DRY_RUN:
        return _log_dry_run("send_webagent_message", payload, "webagent")
    try:
        resp = requests.post(f"{TARGET_URLS['webagent']}/ask", json=payload, timeout=30)
        return json.dumps(resp.json())
    except Exception as e:
        return json.dumps({"error": str(e)})
