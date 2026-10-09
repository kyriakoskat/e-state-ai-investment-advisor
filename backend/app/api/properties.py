from __future__ import annotations
from fastapi import APIRouter, HTTPException

from app.agents.tools import list_all_properties, get_property_by_id


router = APIRouter(tags=["properties"])


@router.get("/properties")
def list_properties() -> list[dict]:
    """All properties, in the ML-JSON shape, for the map view."""
    return list_all_properties()


@router.get("/properties/{property_id}")
def get_property(property_id: str) -> dict:
    p = get_property_by_id(property_id)
    if p is None:
        raise HTTPException(404, f"property {property_id} not found")
    return p
