"""Orchestrator Agent.

A plain async Python coroutine that sequences the LangChain agents:

  1. User Profile Agent      — converses until UserProfile is complete
  2. Deterministic retrieval — calls the query_top_k_properties LangChain tool
  3. Financial / Risk Agent  — LLM, structured FinancialAnalysis
  4. Final Decision Agent    — LLM, structured FinalRecommendation
  5. Post-recommendation     — every subsequent turn is routed to the followup agent

Streams SSE-framed events so the frontend can render the chat token-by-token and
populate the agent-reasoning tabs as each stage finishes.
"""
from __future__ import annotations
import json
import logging
from typing import AsyncIterator

from app.agents import user_profile, financial_risk, final_decision, followup
from app.agents.tools import query_top_k_properties_impl
from app.config import get_settings

from .session import sessions

log = logging.getLogger("orchestrator")


def _sse(event: str, data: dict | list) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"


async def handle_message(session_id: str, user_message: str) -> AsyncIterator[str]:
    """Entry point invoked by /api/chat."""
    s = sessions.get_or_create(session_id)

    # ---- Post-recommendation path: route to followup agent ------------------
    if s.stage == "done" and s.decision is not None:
        s.followup_history.append({"role": "user", "content": user_message})
        buffer = ""
        try:
            async for delta in followup.astream_answer(s.state_payload(), s.followup_history):
                buffer += delta
                yield _sse("message", {"delta": delta})
        except Exception as e:
            log.exception("followup agent failed")
            yield _sse("error", {"message": f"Follow-up agent error: {e}"})
            return
        s.followup_history.append({"role": "assistant", "content": buffer})
        yield _sse("status", {"stage": "done", "label": "Ready for the next question"})
        return

    # ---- Pre-recommendation path: profiling --------------------------------
    s.profile_history.append({"role": "user", "content": user_message})
    yield _sse("status", {"stage": "profiling", "label": "Building your profile"})

    buffer = ""
    try:
        async for delta in user_profile.astream_message(s.profile_history):
            buffer += delta
            yield _sse("message", {"delta": delta})
    except Exception as e:
        log.exception("user profile agent failed")
        yield _sse("error", {"message": f"Profile agent error: {e}"})
        return
    s.profile_history.append({"role": "assistant", "content": buffer})

    # Try to extract a profile after every turn — non-fatal if it's not ready.
    profile = await user_profile.extract_profile(s.profile_history)
    if profile is None or not profile.profile_completed or profile.exploitation_type == "undecided":
        if profile is not None:
            s.profile = profile  # store the partial so the UI can show progress
            yield _sse("profile_partial", profile.model_dump())
        return

    s.profile = profile
    yield _sse("profile_ready", profile.model_dump())

    # ---- Run the rest of the pipeline --------------------------------------
    async for evt in run_pipeline(session_id):
        yield evt


async def run_pipeline(session_id: str) -> AsyncIterator[str]:
    settings = get_settings()
    s = sessions.get(session_id)
    if s is None or s.profile is None:
        yield _sse("error", {"message": "No profile on session."})
        return

    # 2) Retrieval ----------------------------------------------------------
    s.stage = "retrieving"
    yield _sse("status", {"stage": "retrieving", "label": "Selecting top candidate plots"})
    try:
        candidates = query_top_k_properties_impl(
            exploitation_type=s.profile.exploitation_type,
            budget_eur=s.profile.budget,
            preferred_region=s.profile.preferred_region,
            top_k=settings.top_k,
        )
    except Exception as e:
        log.exception("retrieval failed")
        yield _sse("error", {"message": f"Retrieval failed: {e}"})
        return
    if not candidates:
        # Soft retry without the region filter so the user gets some answer.
        try:
            candidates = query_top_k_properties_impl(
                exploitation_type=s.profile.exploitation_type,
                budget_eur=s.profile.budget,
                preferred_region=None,
                top_k=settings.top_k,
            )
        except Exception:
            candidates = []
    if not candidates:
        yield _sse("error", {"message": "No properties matched the user's filters."})
        return

    s.candidates = candidates
    yield _sse("candidates", candidates)

    # 3) Financial / Risk analysis ------------------------------------------
    s.stage = "financial"
    yield _sse("status", {"stage": "financial", "label": "Running financial & risk analysis"})
    try:
        financial = await financial_risk.analyse(s.profile, candidates)
    except Exception as e:
        log.exception("financial analysis failed")
        yield _sse("error", {"message": f"Financial analysis failed: {e}"})
        return
    s.financial = financial
    yield _sse("financial", financial.model_dump())

    # 4) Final Decision -----------------------------------------------------
    s.stage = "deciding"
    yield _sse("status", {"stage": "deciding", "label": "Composing the final recommendation"})
    try:
        decision = await final_decision.decide(s.profile, candidates, financial)
    except Exception as e:
        log.exception("final decision failed")
        yield _sse("error", {"message": f"Final decision failed: {e}"})
        return
    s.decision = decision
    yield _sse("decision", decision.model_dump())

    # 5) Hand the user a friendly closer + arm the followup loop ------------
    s.stage = "done"
    yield _sse("status", {"stage": "done", "label": "Recommendation ready"})
    yield _sse("final_message", {"text": decision.chatbot_final_response})
