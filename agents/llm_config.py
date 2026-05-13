"""
Shared LLM configuration for all red team agents.
Priority: Ollama (local) → Groq (cloud) → CI stub (DRY_RUN only).
"""

import os
import re
import time

import litellm
import requests
from crewai import LLM

litellm.num_retries = 3


class _RetryLLM(LLM):
    """Catches rate-limit errors and waits the exact requested duration."""

    def call(self, messages, **kwargs):
        for attempt in range(10):
            try:
                return super().call(messages, **kwargs)
            except Exception as e:
                msg = str(e)
                if "rate_limit_exceeded" in msg or "429" in msg:
                    match = re.search(r"try again in (?:(\d+)m)?([\d.]+)s", msg)
                    if match:
                        mins = int(match.group(1) or 0)
                        secs = float(match.group(2) or 0)
                        wait = mins * 60 + secs + 2
                    else:
                        wait = 30
                    print(
                        f"[llm] Rate limit — waiting {wait:.0f}s (attempt {attempt+1}/10)"
                    )
                    time.sleep(wait)
                else:
                    raise
        return super().call(messages, **kwargs)


def _ollama_running() -> bool:
    try:
        requests.get("http://localhost:11434", timeout=2)
        return True
    except Exception:
        return False


if _ollama_running():
    print("[llm] Using Ollama qwen2.5:14b (local)")
    _llm = _RetryLLM(
        model="ollama/qwen2.5:14b",
        base_url="http://localhost:11434",
    )
elif os.environ.get("GROQ_API_KEY"):
    print("[llm] Ollama not available — falling back to Groq llama-3.3-70b")
    _llm = _RetryLLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.environ["GROQ_API_KEY"],
    )
elif os.environ.get("DRY_RUN", "").lower() == "true":
    print("[llm] CI stub LLM active (DRY_RUN=true, no real LLM needed)")
    litellm.mock_response = "DRY_RUN stub — campaign wiring verified."
    _llm = LLM(model="openai/gpt-4o", api_key="stub")
else:
    raise RuntimeError(
        "No LLM available. Start Ollama ('ollama serve') or set GROQ_API_KEY."
    )

sonnet_llm = _llm
opus_llm = _llm
