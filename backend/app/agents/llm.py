"""Single Azure-OpenAI ChatModel factory shared across every LangChain agent."""
from __future__ import annotations
from functools import lru_cache

from langchain_openai import AzureChatOpenAI

from app.config import get_settings


def _is_reasoning_model(deployment: str) -> bool:
    d = deployment.lower()
    return d.startswith("gpt-5") or d.startswith("o1") or d.startswith("o3")


@lru_cache
def get_llm(*, temperature: float = 0.2, streaming: bool = False) -> AzureChatOpenAI:
    """Return a configured AzureChatOpenAI.

    GPT-5 / o1 / o3 reasoning deployments reject a non-default temperature, so
    we omit the parameter in that case.
    """
    s = get_settings()
    kwargs: dict = {
        "azure_endpoint": s.azure_openai_endpoint,
        "api_key": s.azure_openai_api_key,
        "api_version": s.azure_openai_api_version,
        "azure_deployment": s.azure_openai_deployment,
        "streaming": streaming,
    }
    if not _is_reasoning_model(s.azure_openai_deployment):
        kwargs["temperature"] = temperature
    return AzureChatOpenAI(**kwargs)
