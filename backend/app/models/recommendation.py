from __future__ import annotations
from pydantic import BaseModel, Field


class FinalRecommendationCore(BaseModel):
    recommended_property_id: str
    rank: int = 1
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_summary: str
    main_reasons: list[str] = Field(default_factory=list)
    possible_concerns: list[str] = Field(default_factory=list)


class RankedProperty(BaseModel):
    property_id: str
    rank: int
    short_explanation: str


class FinalRecommendation(BaseModel):
    """Structured output of the Final Decision Making Agent."""
    final_recommendation: FinalRecommendationCore
    ranked_properties: list[RankedProperty] = Field(default_factory=list)
    chatbot_final_response: str
