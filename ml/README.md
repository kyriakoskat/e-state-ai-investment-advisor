# Hyperspectral analysis notebook

[`hyperspectral_analysis.ipynb`](hyperspectral_analysis.ipynb) is the exploratory notebook developed for the Makeathlon. It is not a reusable production package or a self-contained dataset.

## Contents

1. Browse EnMAP spectral `.TIF` files and associated `METADATA.XML`.
2. Parse per-band wavelengths and identify spectral bands.
3. Calculate NDVI, NDWI, NDMI, NDRE, NBR, GNDVI, MSI, CIRE, GCI, BSI and other indices.
4. Inspect spatial variation and create parcel dashboards.
5. Normalize per-pixel features, run PCA (five components) and K-Means clustering in an exploratory example.
6. Combine plot summaries with PVGIS and wind-resource tables; create weighted heuristic land-use scores.
7. Add **synthetic** infrastructure and terrain factors for the battery-storage and data-center prototype.

## Run (with original challenge inputs)

- Python 3.11 (suggested); install `pip install -r ml/requirements.txt`.
- Set `MAKEATHON_DATA_DIR` to the directory containing the EnMAP scenes, PVGIS CSVs, `wind_power_densities.xlsx`, and any required infrastructure CSVs. The notebook otherwise expects `/content/drive/MyDrive/images_makeathlon`, its original Colab location.
- Run cells in order from Jupyter or Colab. Colab-specific `!pip install` cells may need adjustment locally.

**Not included:** the raw EnMAP scenes, `METADATA.XML` inputs, PVGIS/wind source files, synthetic infrastructure CSV, generated CSV results or chart images beyond the selected example plots under `docs/images/`. Some exact outputs cannot be reproduced from this repository alone.

## Research-prototype limitations

- K-Means/PCA demonstration is shown for the first analyzed scene; it is not a trained supervised predictive model and its cluster IDs have no learned semantic meaning.
- Land-use suitability scores use hand-picked scaling, weights and thresholds. Some late-stage terrain and grid features are synthetic.
- A demo-only `keep_battery_dc_below_wind` heuristic adjusts relative ranking; it should **not** be used for real investment assessments.
- Treat scores, simulated financial estimates and recommended uses as illustrative, not validated investment advice.

Outputs were cleared from the published notebook to reduce file size and avoid including temporary Colab metadata. Figures in `docs/images/` come from the provided notebook's original output cells.
