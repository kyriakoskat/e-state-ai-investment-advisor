"""Seed the `properties` table from the precomputed ML output.

The 4 challenge parcels (Veroia, Arkadia, Arkadia II, Magnisia) are loaded
verbatim from the upstream JSON. 6 synthetic parcels around Greece are added
so the retrieval step can return a meaningful top-k under varied user filters.

Every parcel gets a default 250m x 250m footprint (62 500 m²) priced at €1M, per
product decision (real listings will overwrite these later).
"""
from __future__ import annotations

import json
import math
from typing import Any

from sqlalchemy import text

from app.db.database import engine


DEFAULT_AREA_M2 = 250 * 250  # 62 500
DEFAULT_PRICE_EUR = 1_000_000

_SIDE_M = math.sqrt(DEFAULT_AREA_M2)  # 250 m


def _polygon_around(lat: float, lon: float, side_m: float = _SIDE_M) -> dict:
    """Build a square GeoJSON polygon centered on (lat, lon) for the map layer."""
    dlat = (side_m / 2) / 111_320
    dlon = (side_m / 2) / (111_320 * math.cos(math.radians(lat)))
    return {
        "type": "Polygon",
        "coordinates": [[
            [lon - dlon, lat - dlat],
            [lon + dlon, lat - dlat],
            [lon + dlon, lat + dlat],
            [lon - dlon, lat + dlat],
            [lon - dlon, lat - dlat],
        ]],
    }


# Greek region names per parcel (used by the user-region filter).
# 4 challenge parcels — values straight from the ML JSON.
CHALLENGE_PARCELS: list[dict[str, Any]] = [
    {
        "property_id": "plot_Veroia",
        "plot_name": "Veroia",
        "identity": "high_vegetation_agricultural_asset",
        "region": "Imathia",
        "location": {"latitude": 40.398697, "longitude": 22.120677},
        "image_metadata": {"height": 17, "width": 18, "bands": 224,
                           "source_type": "hyperspectral_image"},
        "spectral_indices": {
            "NDVI": {"mean": 0.849934, "median": 0.882353, "min": 0.461557,
                     "max": 0.894293, "high_vegetation_percentage": 0.99308},
            "NDWI": {"mean": -0.75653},
            "NDMI": {"mean": 0.330731},
            "NDRE": {"mean": 0.397324},
            "NBR":  {"mean": 0.613976},
            "GNDVI": {"mean": 0.75653},
        },
        "terrain_analysis": {
            "slope_degrees": 13,
            "terrain_suitability_score": 32.75,
            "terrain_limitation_label": "moderate_terrain_constraint",
        },
        "investment_scores": {
            "agriculture_score": 91.885757, "pv_score": 50.15375,
            "wind_score": 16.4, "battery_score": 13.4, "data_center_score": 11.4,
        },
        "recommended_use": {"final_recommendation": "agriculture_priority",
                            "confidence": "high"},
        "suggested_crops": ["Ροδάκινα", "Δαμάσκηνα", "Μήλα",
                            "Βερίκοκα", "Κεράσια", "Καρύδια"],
        "risk_flags": ["moderate_terrain_constraint"],
        "agent_ready_summary": {
            "one_liner": "Veroia: agriculture_priority with high confidence.",
            "best_strategy": "agriculture_priority",
        },
    },
    {
        "property_id": "plot_arkadia2",
        "plot_name": "arkadia2",
        "identity": "mixed_use_land_asset_needs_more_context",
        "region": "Arkadia",
        "location": {"latitude": 37.324456, "longitude": 22.143828},
        "image_metadata": {"height": 17, "width": 18, "bands": 224,
                           "source_type": "hyperspectral_image"},
        "spectral_indices": {
            "NDVI": {"mean": 0.620031, "median": 0.64276, "min": 0.150407,
                     "max": 0.854751, "high_vegetation_percentage": 0.809689},
            "NDWI": {"mean": -0.604039},
            "NDMI": {"mean": 0.145349},
            "NDRE": {"mean": 0.273566},
            "NBR":  {"mean": 0.368016},
            "GNDVI": {"mean": 0.604039},
        },
        "terrain_analysis": {
            "slope_degrees": 16,
            "terrain_suitability_score": 26.75,
            "terrain_limitation_label": "high_terrain_constraint",
        },
        "investment_scores": {
            "agriculture_score": 62.540888, "pv_score": 60.004865,
            "wind_score": 27.15832, "battery_score": 24.15832,
            "data_center_score": 22.15832,
        },
        "recommended_use": {"final_recommendation": "mixed_use_or_needs_more_context",
                            "confidence": "low"},
        "suggested_crops": ["Ελιά", "Σιτηρά", "Βρώμη", "Αμπέλια", "Καρύδια"],
        "risk_flags": ["high_terrain_constraint"],
        "agent_ready_summary": {
            "one_liner": "arkadia2: mixed_use_or_needs_more_context with low confidence.",
            "best_strategy": "mixed_use_or_needs_more_context",
        },
    },
    {
        "property_id": "plot_arkadia",
        "plot_name": "arkadia",
        "identity": "low_vegetation_pv_asset",
        "region": "Arkadia",
        "location": {"latitude": 37.651492, "longitude": 22.366139},
        "image_metadata": {"height": 18, "width": 18, "bands": 224,
                           "source_type": "hyperspectral_image"},
        "spectral_indices": {
            "NDVI": {"mean": 0.281865, "median": 0.289446, "min": 0.171875,
                     "max": 0.475995, "high_vegetation_percentage": 0},
            "NDWI": {"mean": -0.387447},
            "NDMI": {"mean": -0.176435},
            "NDRE": {"mean": 0.142209},
            "NBR":  {"mean": -0.031534},
            "GNDVI": {"mean": 0.387447},
        },
        "terrain_analysis": {
            "slope_degrees": 18,
            "terrain_suitability_score": 23.75,
            "terrain_limitation_label": "severe_terrain_constraint",
        },
        "investment_scores": {
            "agriculture_score": 23.183932, "pv_score": 74.6485,
            "wind_score": 30, "battery_score": 27, "data_center_score": 25,
        },
        "recommended_use": {"final_recommendation": "pv_priority",
                            "confidence": "high"},
        "suggested_crops": ["Ελιά", "Σιτηρά", "Βρώμη", "Αμπέλια", "Καρύδια"],
        "risk_flags": ["severe_terrain_constraint", "low_high_vegetation_coverage"],
        "agent_ready_summary": {
            "one_liner": "arkadia: pv_priority with high confidence.",
            "best_strategy": "pv_priority",
        },
    },
    {
        "property_id": "plot_magnisia",
        "plot_name": "magnisia",
        "identity": "low_vegetation_pv_asset",
        "region": "Magnisia",
        "location": {"latitude": 39.174176, "longitude": 22.766325},
        "image_metadata": {"height": 18, "width": 18, "bands": 224,
                           "source_type": "hyperspectral_image"},
        "spectral_indices": {
            "NDVI": {"mean": 0.341716, "median": 0.358568, "min": -0.052326,
                     "max": 0.696335, "high_vegetation_percentage": 0.199219},
            "NDWI": {"mean": -0.436542},
            "NDMI": {"mean": -0.040135},
            "NDRE": {"mean": 0.151262},
            "NBR":  {"mean": 0.116458},
            "GNDVI": {"mean": 0.436542},
        },
        "terrain_analysis": {
            "slope_degrees": 15,
            "terrain_suitability_score": 29.75,
            "terrain_limitation_label": "high_terrain_constraint",
        },
        "investment_scores": {
            "agriculture_score": 35.315514, "pv_score": 68.80509,
            "wind_score": 21.303535, "battery_score": 18.303535,
            "data_center_score": 16.303535,
        },
        "recommended_use": {"final_recommendation": "pv_priority",
                            "confidence": "high"},
        "suggested_crops": ["Ελιά", "Σιτηρά", "Βαμβάκι", "Κριθάρι",
                            "Τομάτα", "Αμυγδαλιά"],
        "risk_flags": ["high_terrain_constraint", "low_high_vegetation_coverage"],
        "agent_ready_summary": {
            "one_liner": "magnisia: pv_priority with high confidence.",
            "best_strategy": "pv_priority",
        },
    },
]


# 6 synthetic parcels so top-k retrieval has alternatives in different regions.
SYNTHETIC_PARCELS: list[dict[str, Any]] = [
    {
        "property_id": "plot_thessaly_basin",
        "plot_name": "Thessaly Basin",
        "identity": "high_vegetation_agricultural_asset",
        "region": "Thessaly",
        "location": {"latitude": 39.638, "longitude": 22.418},
        "image_metadata": {"height": 18, "width": 18, "bands": 224,
                           "source_type": "hyperspectral_image"},
        "spectral_indices": {
            "NDVI": {"mean": 0.78, "median": 0.81, "min": 0.42, "max": 0.88,
                     "high_vegetation_percentage": 0.92},
            "NDWI": {"mean": -0.6}, "NDMI": {"mean": 0.28},
            "NDRE": {"mean": 0.36}, "NBR": {"mean": 0.55}, "GNDVI": {"mean": 0.7},
        },
        "terrain_analysis": {"slope_degrees": 3,
                             "terrain_suitability_score": 41.5,
                             "terrain_limitation_label": "low_terrain_constraint"},
        "investment_scores": {"agriculture_score": 87.4, "pv_score": 58.2,
                              "wind_score": 18.0, "battery_score": 22.0,
                              "data_center_score": 24.0},
        "recommended_use": {"final_recommendation": "agriculture_priority",
                            "confidence": "high"},
        "suggested_crops": ["Βαμβάκι", "Σιτάρι", "Καλαμπόκι"],
        "risk_flags": [],
        "agent_ready_summary": {
            "one_liner": "Thessaly Basin: agriculture_priority with high confidence.",
            "best_strategy": "agriculture_priority"},
    },
    {
        "property_id": "plot_thrace_plains",
        "plot_name": "Thrace Plains",
        "identity": "wind_potential_asset",
        "region": "Evros",
        "location": {"latitude": 41.105, "longitude": 26.182},
        "image_metadata": {"height": 18, "width": 18, "bands": 224,
                           "source_type": "hyperspectral_image"},
        "spectral_indices": {
            "NDVI": {"mean": 0.46, "median": 0.48, "min": 0.10, "max": 0.71,
                     "high_vegetation_percentage": 0.45},
            "NDWI": {"mean": -0.45}, "NDMI": {"mean": 0.10},
            "NDRE": {"mean": 0.20}, "NBR": {"mean": 0.32}, "GNDVI": {"mean": 0.5},
        },
        "terrain_analysis": {"slope_degrees": 4,
                             "terrain_suitability_score": 38.0,
                             "terrain_limitation_label": "low_terrain_constraint"},
        "investment_scores": {"agriculture_score": 55.0, "pv_score": 64.0,
                              "wind_score": 78.5, "battery_score": 52.0,
                              "data_center_score": 34.0},
        "recommended_use": {"final_recommendation": "wind_priority",
                            "confidence": "high"},
        "suggested_crops": ["Σιτηρά", "Αμπέλια"],
        "risk_flags": [],
        "agent_ready_summary": {
            "one_liner": "Thrace Plains: wind_priority with high confidence.",
            "best_strategy": "wind_priority"},
    },
    {
        "property_id": "plot_crete_hills",
        "plot_name": "Heraklion Hills",
        "identity": "low_vegetation_pv_asset",
        "region": "Crete",
        "location": {"latitude": 35.184, "longitude": 25.072},
        "image_metadata": {"height": 18, "width": 18, "bands": 224,
                           "source_type": "hyperspectral_image"},
        "spectral_indices": {
            "NDVI": {"mean": 0.30, "median": 0.31, "min": 0.05, "max": 0.55,
                     "high_vegetation_percentage": 0.08},
            "NDWI": {"mean": -0.5}, "NDMI": {"mean": -0.15},
            "NDRE": {"mean": 0.14}, "NBR": {"mean": -0.02}, "GNDVI": {"mean": 0.4},
        },
        "terrain_analysis": {"slope_degrees": 9,
                             "terrain_suitability_score": 28.0,
                             "terrain_limitation_label": "high_terrain_constraint"},
        "investment_scores": {"agriculture_score": 26.0, "pv_score": 81.0,
                              "wind_score": 42.0, "battery_score": 36.0,
                              "data_center_score": 22.0},
        "recommended_use": {"final_recommendation": "pv_priority",
                            "confidence": "high"},
        "suggested_crops": ["Ελιά", "Αμπέλια"],
        "risk_flags": ["high_terrain_constraint", "low_high_vegetation_coverage"],
        "agent_ready_summary": {
            "one_liner": "Heraklion Hills: pv_priority with high confidence.",
            "best_strategy": "pv_priority"},
    },
    {
        "property_id": "plot_messinia_lowlands",
        "plot_name": "Messinia Lowlands",
        "identity": "high_vegetation_agricultural_asset",
        "region": "Messinia",
        "location": {"latitude": 37.041, "longitude": 21.957},
        "image_metadata": {"height": 18, "width": 18, "bands": 224,
                           "source_type": "hyperspectral_image"},
        "spectral_indices": {
            "NDVI": {"mean": 0.72, "median": 0.74, "min": 0.30, "max": 0.85,
                     "high_vegetation_percentage": 0.88},
            "NDWI": {"mean": -0.55}, "NDMI": {"mean": 0.22},
            "NDRE": {"mean": 0.30}, "NBR": {"mean": 0.5}, "GNDVI": {"mean": 0.65},
        },
        "terrain_analysis": {"slope_degrees": 3,
                             "terrain_suitability_score": 40.0,
                             "terrain_limitation_label": "low_terrain_constraint"},
        "investment_scores": {"agriculture_score": 82.0, "pv_score": 55.0,
                              "wind_score": 20.0, "battery_score": 18.0,
                              "data_center_score": 19.0},
        "recommended_use": {"final_recommendation": "agriculture_priority",
                            "confidence": "high"},
        "suggested_crops": ["Ελιά", "Σιτηρά", "Πορτοκάλια"],
        "risk_flags": [],
        "agent_ready_summary": {
            "one_liner": "Messinia Lowlands: agriculture_priority with high confidence.",
            "best_strategy": "agriculture_priority"},
    },
    {
        "property_id": "plot_kozani_plateau",
        "plot_name": "Kozani Plateau",
        "identity": "industrial_grid_asset",
        "region": "Kozani",
        "location": {"latitude": 40.301, "longitude": 21.788},
        "image_metadata": {"height": 18, "width": 18, "bands": 224,
                           "source_type": "hyperspectral_image"},
        "spectral_indices": {
            "NDVI": {"mean": 0.38, "median": 0.40, "min": 0.08, "max": 0.55,
                     "high_vegetation_percentage": 0.25},
            "NDWI": {"mean": -0.45}, "NDMI": {"mean": 0.05},
            "NDRE": {"mean": 0.18}, "NBR": {"mean": 0.20}, "GNDVI": {"mean": 0.5},
        },
        "terrain_analysis": {"slope_degrees": 4,
                             "terrain_suitability_score": 36.5,
                             "terrain_limitation_label": "low_terrain_constraint"},
        "investment_scores": {"agriculture_score": 38.0, "pv_score": 66.0,
                              "wind_score": 60.0, "battery_score": 71.0,
                              "data_center_score": 65.0},
        "recommended_use": {"final_recommendation": "battery_priority",
                            "confidence": "medium"},
        "suggested_crops": ["Σιτηρά"],
        "risk_flags": [],
        "agent_ready_summary": {
            "one_liner": "Kozani Plateau: battery_priority with medium confidence.",
            "best_strategy": "battery_priority"},
    },
    {
        "property_id": "plot_arta_valley",
        "plot_name": "Arta Valley",
        "identity": "mixed_use_land_asset_needs_more_context",
        "region": "Arta",
        "location": {"latitude": 39.160, "longitude": 20.984},
        "image_metadata": {"height": 18, "width": 18, "bands": 224,
                           "source_type": "hyperspectral_image"},
        "spectral_indices": {
            "NDVI": {"mean": 0.55, "median": 0.57, "min": 0.20, "max": 0.78,
                     "high_vegetation_percentage": 0.61},
            "NDWI": {"mean": -0.52}, "NDMI": {"mean": 0.18},
            "NDRE": {"mean": 0.24}, "NBR": {"mean": 0.40}, "GNDVI": {"mean": 0.58},
        },
        "terrain_analysis": {"slope_degrees": 8,
                             "terrain_suitability_score": 31.5,
                             "terrain_limitation_label": "moderate_terrain_constraint"},
        "investment_scores": {"agriculture_score": 60.0, "pv_score": 52.0,
                              "wind_score": 28.0, "battery_score": 30.0,
                              "data_center_score": 26.0},
        "recommended_use": {"final_recommendation": "mixed_use_or_needs_more_context",
                            "confidence": "medium"},
        "suggested_crops": ["Ελιά", "Πορτοκάλια", "Σιτηρά"],
        "risk_flags": ["moderate_terrain_constraint"],
        "agent_ready_summary": {
            "one_liner": "Arta Valley: mixed_use_or_needs_more_context with medium confidence.",
            "best_strategy": "mixed_use_or_needs_more_context"},
    },
]


def _expand(p: dict[str, Any]) -> dict[str, Any]:
    """Flatten the nested JSON record into a row matching the `properties` table."""
    loc = p["location"]
    img = p["image_metadata"]
    terrain = p["terrain_analysis"]
    scores = p["investment_scores"]
    rec = p["recommended_use"]
    return {
        "property_id": p["property_id"],
        "plot_name": p["plot_name"],
        "identity": p["identity"],
        "region": p["region"],
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
        "geom": json.dumps(_polygon_around(loc["latitude"], loc["longitude"])),
        "area_m2": DEFAULT_AREA_M2,
        "price_eur": DEFAULT_PRICE_EUR,
        "image_height": img["height"],
        "image_width": img["width"],
        "image_bands": img["bands"],
        "image_source_type": img["source_type"],
        "spectral_indices": json.dumps(p["spectral_indices"]),
        "slope_degrees": terrain["slope_degrees"],
        "terrain_suitability_score": terrain["terrain_suitability_score"],
        "terrain_limitation_label": terrain["terrain_limitation_label"],
        "agriculture_score": scores["agriculture_score"],
        "pv_score": scores["pv_score"],
        "wind_score": scores["wind_score"],
        "battery_score": scores["battery_score"],
        "data_center_score": scores["data_center_score"],
        "final_recommendation": rec["final_recommendation"],
        "recommendation_confidence": rec["confidence"],
        "suggested_crops": json.dumps(p["suggested_crops"], ensure_ascii=False),
        "risk_flags": json.dumps(p["risk_flags"]),
        "agent_ready_summary": json.dumps(p["agent_ready_summary"], ensure_ascii=False),
    }


_INSERT = text("""
INSERT INTO properties (
    property_id, plot_name, identity, region, latitude, longitude, geom,
    area_m2, price_eur,
    image_height, image_width, image_bands, image_source_type,
    spectral_indices,
    slope_degrees, terrain_suitability_score, terrain_limitation_label,
    agriculture_score, pv_score, wind_score, battery_score, data_center_score,
    final_recommendation, recommendation_confidence,
    suggested_crops, risk_flags, agent_ready_summary
) VALUES (
    :property_id, :plot_name, :identity, :region, :latitude, :longitude,
    ST_SetSRID(ST_GeomFromGeoJSON(:geom), 4326),
    :area_m2, :price_eur,
    :image_height, :image_width, :image_bands, :image_source_type,
    CAST(:spectral_indices AS jsonb),
    :slope_degrees, :terrain_suitability_score, :terrain_limitation_label,
    :agriculture_score, :pv_score, :wind_score, :battery_score, :data_center_score,
    :final_recommendation, :recommendation_confidence,
    CAST(:suggested_crops AS jsonb),
    CAST(:risk_flags AS jsonb),
    CAST(:agent_ready_summary AS jsonb)
)
ON CONFLICT (property_id) DO NOTHING
""")


def seed_if_empty() -> None:
    with engine.begin() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM properties")).scalar_one()
        if count and count > 0:
            return
        rows = [_expand(p) for p in CHALLENGE_PARCELS + SYNTHETIC_PARCELS]
        for row in rows:
            conn.execute(_INSERT, row)
