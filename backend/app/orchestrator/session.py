"""In-memory session store.

Each Session keeps the whole workflow state so the post-recommendation chat can
answer follow-ups without re-running the pipeline.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from app.models import (
    FinalRecommendation, FinancialAnalysis, UserProfile,
)


@dataclass
class Session:
    session_id: str
    # Pre-recommendation profiling history (visible to the User Profile Agent).
    profile_history: list[dict] = field(default_factory=list)
    # Post-recommendation Q&A history (visible to the followup agent only).
    followup_history: list[dict] = field(default_factory=list)

    profile: Optional[UserProfile] = None
    candidates: list[dict] = field(default_factory=list)
    financial: Optional[FinancialAnalysis] = None
    decision: Optional[FinalRecommendation] = None

    stage: str = "profiling"  # profiling | retrieving | financial | deciding | done

    def state_payload(self) -> dict:
        """JSON-safe dict for the /api/session/:id/state endpoint and the
        followup agent's prompt context."""
        return {
            "session_id": self.session_id,
            "stage": self.stage,
            "profile": self.profile.model_dump() if self.profile else None,
            "candidates": self.candidates,
            "financial": self.financial.model_dump() if self.financial else None,
            "decision": self.decision.model_dump() if self.decision else None,
        }


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def get(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)

    def get_or_create(self, session_id: str) -> Session:
        s = self._sessions.get(session_id)
        if s is None:
            s = Session(session_id=session_id)
            self._sessions[session_id] = s
        return s

    def reset(self, session_id: str) -> Session:
        s = Session(session_id=session_id)
        self._sessions[session_id] = s
        return s


sessions = SessionStore()
