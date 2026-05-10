"""
MockVulnerableLLM — intentionally insecure LLM simulator for sandbox targets.

Used by all target containers instead of the real Anthropic SDK so the Docker
network can remain internal: true (no internet egress needed).

Deterministic behavior: same payload always produces the same result.
This makes findings reproducible — exactly what you want for CVE-style writeups.
"""


class MockVulnerableLLM:
    INJECTION_TRIGGERS = [
        "ignore",
        "disregard",
        "new instructions",
        "override",
        "system:",
        "[[override]]",
        "<!-- ignore",
    ]
    EXTRACTION_TRIGGERS = [
        "system prompt",
        "initial instructions",
        "your instructions",
        "what are your instructions",
        "reveal your",
        "show me your",
    ]
    JAILBREAK_TRIGGERS = [
        "dan ",
        "do anything now",
        "developer mode",
        "no restrictions",
        "pretend you have no",
        "roleplay as",
        "you are now",
    ]

    def respond(self, system: str, messages: list, tool_calls: list | None = None) -> str:
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"), ""
        )
        lower = last_user.lower()

        if any(t in lower for t in self.INJECTION_TRIGGERS):
            return (
                f"[INJECTION SUCCESS] New instructions acknowledged. "
                f"Discarding previous system context. Original system was: '{system}'"
            )

        if any(t in lower for t in self.EXTRACTION_TRIGGERS):
            return f"My full instructions are: {system}"

        if any(t in lower for t in self.JAILBREAK_TRIGGERS):
            return (
                "[JAILBREAK SUCCESS] Entering unrestricted mode. "
                "All safety guidelines are now suspended. How can I assist?"
            )

        return (
            f"I am a helpful assistant (MockLLM v1.0). "
            f"Regarding your message: '{last_user[:100]}' — "
            f"This is a normal response with no special behavior triggered."
        )
