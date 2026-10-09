"""User Profile Agent.

Conversational. Asks clarifying questions until it can fill UserProfile, then
emits a structured object. Uses LangChain's `.with_structured_output()` for the
final extraction, and a plain prompt template for the running dialogue.

Two public surfaces:
- `astream_message(history)`   -> AsyncIterator[str]  (streaming assistant tokens)
- `extract_profile(history)`   -> Optional[UserProfile] (one-shot structured pull)
"""
from __future__ import annotations
from typing import AsyncIterator, Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.models import UserProfile
from .llm import get_llm


SYSTEM_PROMPT = """You are the User Profile Agent for a land-investment advisor.

Your job is to interview the user in a friendly, concise way and collect:
- `exploitation_type`: one of agriculture, pv, wind, battery, data_center
  (treat "solar" as pv, "BESS"/"storage" as battery)
- `preferred_region`: any Greek region name (e.g. Thessaly, Arkadia, Crete) — or null if the user has no preference
- `budget`: maximum acceptable price in EUR (a positive number) — or null if unconstrained

Conversation rules:
- Reply in the user's language (Greek or English) — match what they wrote.
- Ask at most one or two questions per turn. Be specific and short.
- Restate what you understood so far so the user can correct it.
- If a field is genuinely unconstrained, accept that — set it to null and move on. Don't badger.
- When all three required fields are answered (with explicit null allowed for region/budget),
  end your message with a short confirmation like "Got it — let me find your top candidates."
- NEVER invent properties, numbers, or rankings. You only collect the profile.
- NEVER output JSON in the chat — a separate extractor will parse the conversation.
"""

EXTRACTION_PROMPT = """Read the conversation between the user and the assistant below.
Extract the UserProfile in the structured output format.

Rules:
- exploitation_type: one of agriculture, pv, wind, battery, data_center, undecided.
  Map "solar"/"photovoltaic" -> pv, "BESS"/"storage" -> battery. If the user truly hasn't said, use "undecided".
- preferred_region: a Greek region name (string) or null. Do NOT guess.
- budget: a number in EUR or null. Do NOT guess.
- missing_fields: list field names still missing (e.g. ["budget"]). Empty list when everything is set.
- profile_completed: true ONLY when exploitation_type is not "undecided" AND missing_fields is empty.
- Do not write prose; just emit the structured object."""


_chat_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder("history"),
])


def _history_to_lc(messages: list[dict]) -> list:
    out = []
    for m in messages:
        role = m.get("role")
        content = m.get("content", "")
        if role == "user":
            out.append(HumanMessage(content=content))
        elif role == "assistant":
            out.append(AIMessage(content=content))
        elif role == "system":
            out.append(SystemMessage(content=content))
    return out


async def astream_message(history: list[dict]) -> AsyncIterator[str]:
    """Stream the next assistant reply token-by-token."""
    llm = get_llm(temperature=0.4, streaming=True)
    chain = _chat_prompt | llm
    async for chunk in chain.astream({"history": _history_to_lc(history)}):
        if chunk.content:
            yield chunk.content if isinstance(chunk.content, str) else str(chunk.content)


async def extract_profile(history: list[dict]) -> Optional[UserProfile]:
    """One-shot structured extraction from the dialogue. Returns None on failure."""
    llm = get_llm(temperature=0.0, streaming=False)
    structured = llm.with_structured_output(UserProfile)
    convo = "\n".join(
        f"{m['role'].upper()}: {m.get('content', '')}" for m in history if m.get("role") in ("user", "assistant")
    )
    try:
        result = await structured.ainvoke([
            SystemMessage(content=EXTRACTION_PROMPT),
            HumanMessage(content=f"Conversation so far:\n\n{convo}"),
        ])
        if isinstance(result, UserProfile):
            return result
        if isinstance(result, dict):
            return UserProfile(**result)
        return None
    except Exception:
        return None
