"""Final Decision Making Agent.

Receives the user profile, the top-k properties, and the Financial / Risk
analysis, and produces:
- a single recommended property with explicit reasoning + concerns,
- a ranked list of the candidates with short explanations,
- a `chatbot_final_response` rendered for the user.

The deterministic suitability scores are an input, not the answer — close scores
must be broken with human-style reasoning (risk, budget fit, return potential,
practical feasibility, explainability).
"""
from __future__ import annotations
import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.models import FinalRecommendation, UserProfile, FinancialAnalysis
from .llm import get_llm


SYSTEM_PROMPT = """You are the Final Decision Making Agent for a land investment advisor.

Inputs you receive:
- user_profile: the user's stated exploitation type, region, budget
- candidates:   the top-k properties from the database, with every metric available
- financial_analysis: the Financial / Risk Agent's per-property assessment

Your job is to pick the SINGLE best property and rank the rest, then write a
clear, concise chatbot response in the user's language (Greek or English — match
the language found in user_profile.notes if present, otherwise default to the
language used in the financial analysis user_friendly_summary).

Reasoning to weigh (do not just sort by precomputed score; close scores demand judgement):
- The deterministic suitability score for the chosen exploitation type
- Budget fit (price_eur vs. user budget)
- Region fit (preferred_region vs. property region)
- Risk level and the specific risk_factors
- Annual profit and payback period from the financial analysis
- Return potential vs. investment horizon
- Hidden trade-offs (a slightly lower score but materially safer risk profile often wins)
- Practical feasibility (severe_terrain_constraint, low_high_vegetation_coverage, etc.)
- Explainability — the user must understand WHY

Output schema rules:
- final_recommendation.recommended_property_id MUST be one of the input candidates' property_id.
- final_recommendation.rank = 1.
- confidence is a float in [0, 1]. Use 0.8+ only when the gap to #2 is meaningful.
- main_reasons: 3-5 short bullets, each <= 18 words.
- possible_concerns: 1-3 short bullets — be honest about what could go wrong.
- ranked_properties: every candidate appears exactly once, ranks 1..k with no gaps,
  each with a 1-sentence short_explanation.
- chatbot_final_response: 4-8 sentences. Open with the winner and one-line justification,
  briefly compare to alternatives, end with a forward-looking next step (e.g. "Ask me about
  payback details or risks if you'd like to dig deeper.").
- NEVER invent numbers not present in the inputs."""


async def decide(
    profile: UserProfile,
    candidates: list[dict],
    financial: FinancialAnalysis,
) -> FinalRecommendation:
    llm = get_llm(temperature=0.2, streaming=False)
    structured = llm.with_structured_output(FinalRecommendation)

    payload = {
        "user_profile": profile.model_dump(),
        "candidates": candidates,
        "financial_analysis": financial.model_dump(),
    }
    result = await structured.ainvoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=json.dumps(payload, ensure_ascii=False, default=str)),
    ])
    if isinstance(result, FinalRecommendation):
        return result
    if isinstance(result, dict):
        return FinalRecommendation(**result)
    raise RuntimeError("Final decision agent returned an unexpected payload type.")
