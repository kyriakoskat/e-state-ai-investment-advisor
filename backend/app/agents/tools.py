"""LangChain tools the orchestrator and agents call.

Only one tool is exposed to LLMs: the deterministic PostgreSQL retriever.
Agents are never trusted with raw SQL — they pass parameters and get JSON back.
"""
from __future__ import annotations
from typing import Optional, Literal

from langchain_core.tools import tool
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.db.database import engine
from app.models import SCORE_COLUMN


# Accepted exploitation labels exposed to the LLM. Strings only — no enums in the
# tool schema, since some Azure deployments serialize them awkwardly.
_VALID = ", ".join(sorted(set(SCORE_COLUMN.keys())))


class TopKArgs(BaseModel):
    exploitation_type: str = Field(
        description=(
            f"User's chosen exploitation. One of: {_VALID}. "
            "Use 'pv' for solar / photovoltaic and 'battery' for BESS / storage."
        )
    )
    budget_eur: Optional[float] = Field(
        default=None,
        description="Maximum acceptable price in EUR. Omit (null) when the user has no cap.",
    )
    preferred_region: Optional[str] = Field(
        default=None,
        description=(
            "Region name from the user profile. Case-insensitive substring match against "
            "the `region` column. Omit / null = any region."
        ),
    )
    top_k: int = Field(default=3, ge=1, le=10)


_SELECT_SQL = """
SELECT
    property_id, plot_name, identity, region, latitude, longitude,
    area_m2, price_eur,
    image_height, image_width, image_bands, image_source_type,
    spectral_indices,
    slope_degrees, terrain_suitability_score, terrain_limitation_label,
    agriculture_score, pv_score, wind_score, battery_score, data_center_score,
    final_recommendation, recommendation_confidence,
    suggested_crops, risk_flags, agent_ready_summary,
    ST_AsGeoJSON(geom)::json AS geometry,
    {score_col} AS _score
FROM properties
WHERE 1=1
  {budget_clause}
  {region_clause}
ORDER BY {score_col} DESC NULLS LAST
LIMIT :top_k
"""


def _row_to_property_dict(row: dict) -> dict:
    """Reshape a flat row to the nested ML-JSON contract the agents consume."""
    return {
        "property_id": row["property_id"],
        "plot_name":   row["plot_name"],
        "identity":    row["identity"],
        "region":      row["region"],
        "location":    {"latitude": row["latitude"], "longitude": row["longitude"]},
        "area_m2":     row["area_m2"],
        "price_eur":   row["price_eur"],
        "image_metadata": {
            "height": row["image_height"], "width": row["image_width"],
            "bands": row["image_bands"], "source_type": row["image_source_type"],
        },
        "spectral_indices": row["spectral_indices"],
        "terrain_analysis": {
            "slope_degrees": row["slope_degrees"],
            "terrain_suitability_score": row["terrain_suitability_score"],
            "terrain_limitation_label": row["terrain_limitation_label"],
        },
        "investment_scores": {
            "agriculture_score": row["agriculture_score"],
            "pv_score":          row["pv_score"],
            "wind_score":        row["wind_score"],
            "battery_score":     row["battery_score"],
            "data_center_score": row["data_center_score"],
        },
        "recommended_use": {
            "final_recommendation": row["final_recommendation"],
            "confidence": row["recommendation_confidence"],
        },
        "suggested_crops":     row["suggested_crops"],
        "risk_flags":          row["risk_flags"],
        "agent_ready_summary": row["agent_ready_summary"],
        "geometry":            row.get("geometry"),
    }


def query_top_k_properties_impl(
    exploitation_type: str,
    budget_eur: Optional[float],
    preferred_region: Optional[str],
    top_k: int,
) -> list[dict]:
    """The actual DB-bound implementation. Called both from the LangChain tool
    and directly from the Orchestrator (which needs the raw list, not a string)."""
    score_col = SCORE_COLUMN.get(exploitation_type.lower())
    if not score_col:
        raise ValueError(
            f"Unknown exploitation_type {exploitation_type!r}. Allowed: {_VALID}"
        )

    params: dict = {"top_k": top_k}
    budget_clause = ""
    region_clause = ""
    if budget_eur is not None:
        budget_clause = "AND price_eur <= :budget"
        params["budget"] = float(budget_eur)
    if preferred_region:
        region_clause = "AND region ILIKE :region"
        params["region"] = f"%{preferred_region.strip()}%"

    sql = _SELECT_SQL.format(
        score_col=score_col,
        budget_clause=budget_clause,
        region_clause=region_clause,
    )
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).mappings().all()
    return [_row_to_property_dict(dict(r)) for r in rows]


@tool("query_top_k_properties", args_schema=TopKArgs)
def query_top_k_properties(
    exploitation_type: str,
    budget_eur: Optional[float] = None,
    preferred_region: Optional[str] = None,
    top_k: int = 3,
) -> list[dict]:
    """Retrieve the top-k land plots from PostgreSQL.

    Filters by budget (price_eur <= budget) and region (case-insensitive ILIKE),
    then orders by the precomputed score column matching `exploitation_type`.
    Returns one JSON dict per property with the full metric set.
    """
    return query_top_k_properties_impl(
        exploitation_type=exploitation_type,
        budget_eur=budget_eur,
        preferred_region=preferred_region,
        top_k=top_k,
    )


def list_all_properties() -> list[dict]:
    """Used by the /api/properties endpoint to populate the map."""
    sql = _SELECT_SQL.format(
        score_col="terrain_suitability_score",
        budget_clause="",
        region_clause="",
    ).replace("LIMIT :top_k", "")
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).mappings().all()
    return [_row_to_property_dict(dict(r)) for r in rows]


def get_property_by_id(property_id: str) -> Optional[dict]:
    sql = """
    SELECT
        property_id, plot_name, identity, region, latitude, longitude,
        area_m2, price_eur,
        image_height, image_width, image_bands, image_source_type,
        spectral_indices,
        slope_degrees, terrain_suitability_score, terrain_limitation_label,
        agriculture_score, pv_score, wind_score, battery_score, data_center_score,
        final_recommendation, recommendation_confidence,
        suggested_crops, risk_flags, agent_ready_summary,
        ST_AsGeoJSON(geom)::json AS geometry
    FROM properties
    WHERE property_id = :pid
    """
    with engine.connect() as conn:
        row = conn.execute(text(sql), {"pid": property_id}).mappings().first()
    return _row_to_property_dict(dict(row)) if row else None
