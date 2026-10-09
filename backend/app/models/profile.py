from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field


ExploitationType = Literal[
    "agriculture", "pv", "wind", "battery", "data_center", "undecided"
]


class UserProfile(BaseModel):
    """Structured output of the User Profile Agent."""
    user_id: Optional[str] = None
    intent: Literal["land_investment_recommendation"] = "land_investment_recommendation"
    exploitation_type: ExploitationType = "undecided"
    preferred_region: Optional[str] = Field(
        default=None,
        description='Region name (e.g. "Thessaly", "Arkadia"). Use null when the user has no preference.',
    )
    budget: Optional[float] = Field(
        default=None,
        description="Maximum acceptable price in EUR.",
    )
    missing_fields: list[str] = Field(default_factory=list)
    profile_completed: bool = False
    notes: Optional[str] = Field(
        default=None,
        description="Free-form context the agent extracted but is not part of the structured fields.",
    )
