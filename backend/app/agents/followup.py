"""Post-recommendation follow-up chat.

After the orchestrator has produced a FinalRecommendation, all later turns route
through here. The agent has access to the full session state via the prompt and
answers free-form questions ("why this one?", "compare 1 and 2", "what about
risks?") without restarting the pipeline.

Streaming, so the UI can render token-by-token.
"""
from __future__ import annotations
import json
from typing import AsyncIterator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from .llm import get_llm


SYSTEM_TEMPLATE = """You are the Investment Copilot continuing a conversation after a
land-investment recommendation has been produced. Answer the user's follow-up
questions clearly and concisely, reasoning ONLY from the structured context
below — never invent values.

User profile:
{profile_json}

Top-k candidate properties:
{candidates_json}

Financial Potential / Risk Agent output:
{financial_json}

Final Decision Agent output:
{decision_json}

Style:
- Reply in the same language the user is writing in (Greek or English).
- Be concise: bullets when comparing, short paragraphs when explaining.
- Reference specific numbers and property names from the context.
- If the user asks something the context cannot answer (e.g. "what's the market price of
  almonds in Crete?"), say so honestly rather than guessing.
- Do NOT restart the pipeline. If the user changes the budget / region / exploitation,
  briefly explain that a fresh search is needed and suggest they say so explicitly.
"""


def _render_system(state: dict) -> str:
    def j(obj):
        return json.dumps(obj, ensure_ascii=False, indent=2, default=str)
    return SYSTEM_TEMPLATE.format(
        profile_json=j(state.get("profile")),
        candidates_json=j(state.get("candidates")),
        financial_json=j(state.get("financial")),
        decision_json=j(state.get("decision")),
    )


async def astream_answer(state: dict, history: list[dict]) -> AsyncIterator[str]:
    """Stream the assistant's answer. `history` is the post-recommendation
    conversation so far (turns BEFORE the recommendation are intentionally omitted)."""
    llm = get_llm(temperature=0.3, streaming=True)
    messages = [SystemMessage(content=_render_system(state))]
    for m in history:
        role = m.get("role")
        content = m.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    async for chunk in llm.astream(messages):
        if chunk.content:
            yield chunk.content if isinstance(chunk.content, str) else str(chunk.content)
