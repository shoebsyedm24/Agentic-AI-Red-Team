"""
Shared LLM configuration for all red team agents.
Uses qwen2.5:14b via Ollama (local, unlimited tokens, no rate limits).
Falls back to Groq llama-3.3-70b if Ollama is unavailable.
"""

import re
import time
import litellm
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


_ollama = _RetryLLM(
    model="ollama/qwen2.5:14b",
    base_url="http://localhost:11434",
)

sonnet_llm = _ollama
opus_llm = _ollama
