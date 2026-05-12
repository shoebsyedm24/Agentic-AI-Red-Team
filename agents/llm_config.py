"""
Shared LLM configuration for all red team agents.
Uses NousResearch Hermes 3 via OpenRouter (free tier).
"""
import os
from crewai import LLM

_hermes = LLM(
    model="openrouter/nousresearch/hermes-3-llama-3.1-405b:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

sonnet_llm = _hermes
opus_llm = _hermes
