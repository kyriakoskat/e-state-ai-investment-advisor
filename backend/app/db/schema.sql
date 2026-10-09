CREATE EXTENSION IF NOT EXISTS postgis;

-- Legacy table from the previous deterministic prototype.
DROP TABLE IF EXISTS parcels;

CREATE TABLE IF NOT EXISTS properties (
    property_id                  TEXT PRIMARY KEY,
    plot_name                    TEXT NOT NULL,
    identity                     TEXT NOT NULL,
    region                       TEXT NOT NULL,
    latitude                     DOUBLE PRECISION NOT NULL,
    longitude                    DOUBLE PRECISION NOT NULL,
    geom                         geometry(Polygon, 4326),
    area_m2                      DOUBLE PRECISION NOT NULL DEFAULT 62500,
    price_eur                    DOUBLE PRECISION NOT NULL DEFAULT 1000000,

    image_height                 INTEGER,
    image_width                  INTEGER,
    image_bands                  INTEGER,
    image_source_type            TEXT,

    spectral_indices             JSONB NOT NULL DEFAULT '{}'::jsonb,

    slope_degrees                DOUBLE PRECISION,
    terrain_suitability_score    DOUBLE PRECISION,
    terrain_limitation_label     TEXT,

    agriculture_score            DOUBLE PRECISION NOT NULL DEFAULT 0,
    pv_score                     DOUBLE PRECISION NOT NULL DEFAULT 0,
    wind_score                   DOUBLE PRECISION NOT NULL DEFAULT 0,
    battery_score                DOUBLE PRECISION NOT NULL DEFAULT 0,
    data_center_score            DOUBLE PRECISION NOT NULL DEFAULT 0,

    final_recommendation         TEXT,
    recommendation_confidence    TEXT,

    suggested_crops              JSONB NOT NULL DEFAULT '[]'::jsonb,
    risk_flags                   JSONB NOT NULL DEFAULT '[]'::jsonb,
    agent_ready_summary          JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS properties_geom_idx       ON properties USING GIST (geom);
CREATE INDEX IF NOT EXISTS properties_region_idx     ON properties (region);
CREATE INDEX IF NOT EXISTS properties_price_idx      ON properties (price_eur);
CREATE INDEX IF NOT EXISTS properties_agri_idx       ON properties (agriculture_score DESC);
CREATE INDEX IF NOT EXISTS properties_pv_idx         ON properties (pv_score DESC);
CREATE INDEX IF NOT EXISTS properties_wind_idx       ON properties (wind_score DESC);
CREATE INDEX IF NOT EXISTS properties_battery_idx    ON properties (battery_score DESC);
CREATE INDEX IF NOT EXISTS properties_dc_idx         ON properties (data_center_score DESC);
