from __future__ import annotations
import uuid
from fastapi import APIRouter, HTTPException

from app.orchestrator.session import sessions


router = APIRouter(tags=["session"])


@router.post("/session")
def create_session() -> dict:
    sid = str(uuid.uuid4())
    sessions.get_or_create(sid)
    return {"session_id": sid}


@router.post("/session/{session_id}/reset")
def reset_session(session_id: str) -> dict:
    sessions.reset(session_id)
    return {"session_id": session_id, "stage": "profiling"}


@router.get("/session/{session_id}/state")
def get_session_state(session_id: str) -> dict:
    """Full workflow state for the Financial / Final Decision agent tabs."""
    s = sessions.get(session_id)
    if s is None:
        # Empty placeholder so the UI can render the loading state without 404 noise.
        return {
            "session_id": session_id, "stage": "profiling",
            "profile": None, "candidates": [], "financial": None, "decision": None,
        }
    return s.state_payload()


@router.get("/session/{session_id}/recommendation")
def get_recommendation(session_id: str):
    s = sessions.get(session_id)
    if s is None or s.decision is None:
        raise HTTPException(404, "Recommendation not available for this session.")
    return s.decision
