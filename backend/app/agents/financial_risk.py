"""Financial Potential / Risk Agent.

Takes the user profile + the top-k properties (already retrieved from PostgreSQL)
and produces one structured FinancialAnalysisItem per property, covering capex,
opex, revenue, payback, risks, opportunities, and a user-friendly summary.

The exploitation type drives which factors the prompt asks the LLM to weigh.
"""
from __future__ import annotations
import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.models import FinancialAnalysis, UserProfile
from .llm import get_llm


SYSTEM_PROMPT = """You are the Financial Potential and Risk Agent for a land investment advisor.

You receive:
- a user profile (exploitation type, region, budget)
- a list of top-k candidate properties with full ML-derived metrics
  (spectral indices, terrain, precomputed investment scores, suggested crops, risk flags)

For EACH property, produce one entry in `financial_analysis` with:
- property_id (echo as-is)
- exploitation_type (echo the user's choice — e.g. "agriculture", "pv", "wind", "battery", "data_center")
- estimated_initial_investment_eur  (one-time CAPEX in EUR)
- estimated_annual_revenue_eur      (gross EUR/year)
- estimated_annual_operating_cost_eur (EUR/year)
- estimated_net_annual_profit_eur   (revenue - opex)
- estimated_payback_period_years    (CAPEX / max(net_profit, 1); cap at 50)
- risk_level  (low | medium | high)
- risk_factors (3-6 concise bullet strings)
- opportunities (2-5 concise bullet strings)
- user_friendly_summary (2-3 sentences for a non-expert investor)

What to consider per exploitation type:

- agriculture: NDVI / GNDVI vegetation strength, NDMI moisture, slope, region climate,
  suitability of `suggested_crops`, approximate market price per crop, drought/water risk,
  soil quality proxies, labour and machinery opex. Assume 250 000 m² (25 ha) plot.

- pv (solar): solar radiation proxies (low NDVI + low cloud regions correlate with high GHI),
  slope_degrees, terrain_suitability_score, proximity-to-grid assumption (use the user's region
  to reason qualitatively; you do not have a substation distance field), area, regulatory risk,
  installation cost ~600-900 €/kWp installed, yearly energy ~1400-1700 kWh/kWp in Greece.

- wind: wind potential is correlated with high-altitude / open-plain regions like Thrace, Crete,
  Aegean islands; flat low-NDVI sites are more credible. CAPEX is high (~1.2-1.5 M€/MW).

- battery (BESS): grid proximity, electricity market arbitrage potential, regulatory regime,
  CAPEX ~300-500 €/kWh, cycling opex.

- data_center: power availability, fibre / connectivity (assume major urban regions = good),
  cooling demand (cooler regions cheaper), seismic risk, road access. CAPEX dominates.

Rules:
- Always reason from the structured data the user gives you. Do NOT invent missing metrics.
- All currency numbers are integers or floats in EUR. No strings.
- The output MUST conform to the FinancialAnalysis schema. Emit exactly one entry per input property.
- Match the order of the input properties.
- Keep the user_friendly_summary jargon-light."""


async def analyse(profile: UserProfile, properties: list[dict]) -> FinancialAnalysis:
    """Run the LLM with structured output, returning a FinancialAnalysis."""
    llm = get_llm(temperature=0.2, streaming=False)
    structured = llm.with_structured_output(FinancialAnalysis)

    payload = {
        "user_profile": profile.model_dump(),
        "properties": properties,
    }
    result = await structured.ainvoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=json.dumps(payload, ensure_ascii=False, default=str)),
    ])
    if isinstance(result, FinancialAnalysis):
        return result
    if isinstance(result, dict):
        return FinancialAnalysis(**result)
    raise RuntimeError("Financial agent returned an unexpected payload type.")
