"""
Shared LLM configuration for all red team agents.
Uses Ollama (local, free) via its OpenAI-compatible API endpoint.
"""
from crewai import LLM

_ollama = LLM(
    model="ollama/llama3.1:8b",
    base_url="http://localhost:11434",
    api_key="ollama",
)

sonnet_llm = _ollama
opus_llm = _ollama
