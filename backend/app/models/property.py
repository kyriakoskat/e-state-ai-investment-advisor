from __future__ import annotations
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


ExploitationType = Literal["agriculture", "pv", "wind", "battery", "data_center"]
SCORE_COLUMN: dict[str, str] = {
    "agriculture": "agriculture_score",
    "pv":          "pv_score",
    "solar":       "pv_score",     # accepted alias from the user-facing language
    "wind":        "wind_score",
    "battery":     "battery_score",
    "bess":        "battery_score",
    "data_center": "data_center_score",
}


class NDVIIndex(BaseModel):
    mean: float
    median: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    high_vegetation_percentage: Optional[float] = None


class ScalarIndex(BaseModel):
    mean: float


class SpectralIndices(BaseModel):
    NDVI: Optional[NDVIIndex] = None
    NDWI: Optional[ScalarIndex] = None
    NDMI: Optional[ScalarIndex] = None
    NDRE: Optional[ScalarIndex] = None
    NBR:  Optional[ScalarIndex] = None
    GNDVI: Optional[ScalarIndex] = None


class TerrainAnalysis(BaseModel):
    slope_degrees: Optional[float] = None
    terrain_suitability_score: Optional[float] = None
    terrain_limitation_label: Optional[str] = None


class InvestmentScores(BaseModel):
    agriculture_score: float = 0.0
    pv_score: float = 0.0
    wind_score: float = 0.0
    battery_score: float = 0.0
    data_center_score: float = 0.0


class RecommendedUse(BaseModel):
    final_recommendation: Optional[str] = None
    confidence: Optional[str] = None


class AgentReadySummary(BaseModel):
    one_liner: Optional[str] = None
    best_strategy: Optional[str] = None


class ImageMetadata(BaseModel):
    height: Optional[int] = None
    width: Optional[int] = None
    bands: Optional[int] = None
    source_type: Optional[str] = None


class Location(BaseModel):
    latitude: float
    longitude: float


class Property(BaseModel):
    """One row of the `properties` table, shaped like the upstream ML JSON."""
    property_id: str
    plot_name: str
    identity: str
    region: str
    location: Location
    area_m2: float
    price_eur: float
    image_metadata: ImageMetadata = Field(default_factory=ImageMetadata)
    spectral_indices: SpectralIndices = Field(default_factory=SpectralIndices)
    terrain_analysis: TerrainAnalysis = Field(default_factory=TerrainAnalysis)
    investment_scores: InvestmentScores = Field(default_factory=InvestmentScores)
    recommended_use: RecommendedUse = Field(default_factory=RecommendedUse)
    suggested_crops: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    agent_ready_summary: AgentReadySummary = Field(default_factory=AgentReadySummary)
    geometry: Optional[dict[str, Any]] = None
