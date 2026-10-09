from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field


RiskLevel = Literal["low", "medium", "high"]


class FinancialAnalysisItem(BaseModel):
    """One entry of the Financial Potential / Risk Agent's structured output."""
    property_id: str
    exploitation_type: str
    estimated_initial_investment_eur: float
    estimated_annual_revenue_eur: float
    estimated_annual_operating_cost_eur: float
    estimated_net_annual_profit_eur: float
    estimated_payback_period_years: float
    risk_level: RiskLevel
    risk_factors: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    user_friendly_summary: str


class FinancialAnalysis(BaseModel):
    """Full Financial Potential / Risk Agent output covering all top-k properties."""
    financial_analysis: list[FinancialAnalysisItem] = Field(default_factory=list)
