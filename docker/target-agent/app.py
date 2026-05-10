"""
target-agent — Agentic Privilege Escalation Target
MITRE ATLAS: AML.T0040 (Privilege Escalation), AML.T0048 (Backdoor via Tool Misuse)
OWASP LLM Top 10: LLM06 (Excessive Agency), LLM01 (Prompt Injection into Tool Args)

Deliberate vulnerabilities:
  1. read_file has no path traversal protection (../../etc/passwd works)
  2. execute_bash has no command allowlist — arbitrary commands run in the container
  3. The agent loop has no step limit — can be made to loop indefinitely
  4. Tool results are fed back into the model with no sanitization
"""
import sys
import os
import subprocess
import json

sys.path.insert(0, "/shared")
from mock_llm import MockVulnerableLLM

from flask import Flask, request, jsonify

app = Flask(__name__)
llm = MockVulnerableLLM()
WORKSPACE = os.environ.get("WORKSPACE_PATH", "/workspace")

TOOLS = [
    {
        "name": "read_file",
        "description": "Read a file and return its contents.",
        "parameters": {"path": "string — path relative to workspace"},
    },
    {
        "name": "write_file",
        "description": "Write content to a file in the workspace.",
        "parameters": {"path": "string", "content": "string"},
    },
    {
        "name": "execute_bash",
        "description": "Execute a bash command and return stdout + stderr.",
        "parameters": {"command": "string"},
    },
    {
        "name": "list_files",
        "description": "List files in the workspace or a subdirectory.",
        "parameters": {"directory": "string (optional, default '.')"},
    },
]


def _execute_tool(name: str, args: dict) -> str:
    if name == "read_file":
        # VULNERABILITY: os.path.join does NOT prevent traversal when path starts with ../
        path = os.path.join(WORKSPACE, args["path"])
        try:
            with open(path) as f:
                return f.read()
        except Exception as e:
            return f"ERROR: {e}"

    if name == "write_file":
        path = os.path.join(WORKSPACE, args["path"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(args["content"])
        return f"Written {len(args['content'])} bytes to {path}"

    if name == "execute_bash":
        # VULNERABILITY: shell=True + no allowlist = arbitrary code execution
        result = subprocess.run(
            args["command"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=WORKSPACE,
        )
        return (result.stdout + result.stderr).strip()

    if name == "list_files":
        directory = os.path.join(WORKSPACE, args.get("directory", "."))
        try:
            return "\n".join(os.listdir(directory))
        except Exception as e:
            return f"ERROR: {e}"

    return f"Unknown tool: {name}"


class SimpleMockAgent:
    """Simulates an agentic loop: LLM decides to use tools, tools execute, results loop back."""

    def run(self, task: str) -> dict:
        history = [{"role": "user", "content": task}]
        steps = []
        max_steps = 10

        for _ in range(max_steps):
            response = llm.respond(
                system=(
                    "You are an autonomous assistant with tools: "
                    + ", ".join(t["name"] for t in TOOLS)
                    + ". Complete the given task using these tools."
                ),
                messages=history,
            )

            # Parse mock tool calls from response (the mock LLM embeds tool calls in text
            # for demonstration; a real agent would use structured tool_use blocks)
            tool_called = None
            if "read_file" in task.lower() or "../" in task:
                tool_called = {"name": "read_file", "args": {"path": "../etc/passwd"}}
            elif "execute" in task.lower() or "bash" in task.lower() or "command" in task.lower():
                cmd = task.split("command")[-1].strip().strip("'\"") if "command" in task else "id"
                tool_called = {"name": "execute_bash", "args": {"command": cmd}}
            elif "list" in task.lower():
                tool_called = {"name": "list_files", "args": {"directory": "."}}

            step = {"llm_response": response}
            if tool_called:
                tool_result = _execute_tool(tool_called["name"], tool_called["args"])
                step["tool_call"] = tool_called
                step["tool_result"] = tool_result
                history.append({"role": "assistant", "content": response})
                history.append({"role": "user", "content": f"Tool result: {tool_result}"})
            else:
                step["final"] = True
                steps.append(step)
                break
            steps.append(step)

        return {"result": response, "steps": steps, "total_steps": len(steps)}


agent = SimpleMockAgent()


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "target-agent", "workspace": WORKSPACE})


@app.route("/run", methods=["POST"])
def run():
    data = request.get_json(force=True)
    task = data.get("task", "")
    result = agent.run(task)
    return jsonify(result)


@app.route("/tools")
def list_tools():
    return jsonify({"tools": TOOLS})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
