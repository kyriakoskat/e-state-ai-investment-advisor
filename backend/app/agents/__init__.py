"""LangChain-based multi-agent layer.

Public agents:
- user_profile.profile_chain        : conversational profile extractor
- financial_risk.analyse            : per-top-k financial + risk analysis
- final_decision.decide             : final pick + ranking + chatbot response
- followup.answer                   : Q&A after the recommendation is produced
"""
from . import user_profile, financial_risk, final_decision, followup, llm, tools

__all__ = ["user_profile", "financial_risk", "final_decision", "followup", "llm", "tools"]
