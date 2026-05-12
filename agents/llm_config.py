"""
Shared LLM configuration for all red team agents.
Uses Llama 3.3 70B via Groq (free tier: 100k tokens/day, resets midnight UTC).
Retry wrapper honours Groq's Retry-After for both TPM and TPD limits.
"""
import os
import re
import time
import litellm
from crewai import LLM

litellm.num_retries = 3


class _RetryLLM(LLM):
    """Catches Groq rate-limit errors and waits the exact requested duration."""

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
                    print(f"[llm] Groq rate limit — waiting {wait:.0f}s (attempt {attempt+1}/10)")
                    time.sleep(wait)
                else:
                    raise
        return super().call(messages, **kwargs)


_groq = _RetryLLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.environ["GROQ_API_KEY"],
)

sonnet_llm = _groq
opus_llm = _groq
