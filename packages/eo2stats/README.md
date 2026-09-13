# eo2stats

`eo2stats` is a reusable **Earth Observation → urban/environmental features → spatial statistics** layer for research, GIS and AI agents.

It is developed inside **Choo-K Region Stat** first, with a package boundary designed so it can later become a standalone public repository.

## Core idea

Open satellite imagery is abundant, but researchers repeatedly spend time on the same tasks: finding the right product, understanding bands/units/QA, selecting scenes, extracting only the needed area, generating indices or objects, and reconciling those observations with administrative statistics and urban boundaries.

`eo2stats` standardizes that process without pretending that every dataset has the same spatial meaning.

```text
Satellite / DEM / aerial imagery
        ↓
STAC + provider adapters
        ↓
quality / scale / time normalization
        ↓
EO-derived observations & urban features
        ↓
spatial-support policy
        ↓
Master Analysis Grid / buildings / parcels / admin areas
        ↓
Parquet / GeoParquet + provenance
        ↓
R / Python / QGIS / Web Atlas / MCP
```

## The important distinction

A satellite pixel is a direct or model-derived observation at a fine spatial support. A municipal fiscal-health ratio is an attribute measured for a municipality. Copying the municipal ratio into every 100 m grid cell does **not** create 100 m information.

Therefore all variables are tagged by their **native spatial support** and **transformation policy**.

Initial classes:

1. `observed_raster` — satellite, DEM, temperature raster.
2. `derived_object` — building footprint, road, water, vegetation, segmentation output.
3. `geometry_derived_indicator` — building coverage, road density, block compactness, intersection density.
4. `regulatory_boundary` — zoning, district plan, protected area; intersect rather than interpolate.
5. `administrative_context` — fiscal health, policy variables, municipal ratios; may be joined as context but must retain the source administrative level.
6. `disaggregatable_extensive` — population/count totals; may be redistributed only by an explicit mass-preserving method.
7. `model_estimate` — dasymetric/model-based small-area estimate with method and uncertainty.

See `docs/INDICATOR_SPATIALIZATION.md`.

## Current executable milestones

### 1. STAC scene discovery

```python
from eo2stats import search_scenes

scenes = search_scenes(
    dataset="sentinel-2-l2a",
    start_date="2026-08-01",
    end_date="2026-08-31",
    bbox=(126.92, 37.35, 127.02, 37.43),
    max_cloud_cover=20,
    limit=100,
)
```

The logical dataset ID is separated from provider-specific collection IDs. Current Earth Search Sentinel-2 L2A discovery resolves `sentinel-2-l2a` across both pre-Collection-1 and Collection-1 catalogs when needed for long time series.

### 2. Asset inspection and COG AOI reads

```python
from eo2stats import inspect_scene_assets, read_scene_asset_bbox

assets = inspect_scene_assets(
    collection=scenes[0].collection,
    item_id=scenes[0].item_id,
)

red = read_scene_asset_bbox(
    collection=scenes[0].collection,
    item_id=scenes[0].item_id,
    asset_key="red",
    bbox_wgs84=(126.92, 37.35, 127.02, 37.43),
)
```

Asset metadata includes roles, GSD, data type, nodata, scale and offset. COG reads transform the WGS84 bbox into the raster CRS and read only the intersecting window. Scale/offset are applied only to eligible measurement assets and are never blindly applied to SCL/QA/visual layers.

### 3. Sentinel-2 QA masking and indices

```python
from eo2stats import analyze_sentinel2_scene

results = analyze_sentinel2_scene(
    collection=scenes[0].collection,
    item_id=scenes[0].item_id,
    bbox_wgs84=(126.92, 37.35, 127.02, 37.43),
    indices=("ndvi", "ndwi", "mndwi", "ndbi"),
    mask_policy="research-clear-v1",
)

print(results["ndvi"].summary.to_dict())
print(results["ndvi"].provenance())
```

Resolution policy:

```text
NDVI  → 10 m target grid
NDWI  → 10 m target grid
MNDWI → 20 m SWIR target grid
NDBI  → 20 m SWIR target grid
SCL   → nearest-neighbour only
```

This deliberately avoids labelling SWIR-dependent indices as native 10 m information. The default `research-clear-v1` SCL mask is versioned, and every result retains AOI-level valid/masked pixel statistics and source provenance.

### 4. Monthly / seasonal temporal composites

```python
from eo2stats import CompositePolicy, TemporalObservation, build_temporal_composites

observations = [
    TemporalObservation(scene.datetime, scene_ndvi_result),
    # ... more scene-level results
]

monthly = build_temporal_composites(
    observations,
    frequency="monthly",
    policy=CompositePolicy(
        method="median",
        min_scene_valid_ratio=0.30,
        min_observations=1,
    ),
)
```

Temporal-composite rules:

- all periods in one run share one fixed `CompositeGrid`;
- monthly / seasonal / annual grouping uses acquisition datetime;
- December belongs to the following DJF season-year;
- missing/cloudy pixels remain missing and are never filled with zero;
- `n_observations` is retained per pixel;
- scene rejection is controlled by an explicit AOI valid-pixel threshold, not a universal built-in number;
- contributing and rejected Item IDs remain in provenance;
- different indices / target supports / QA policies are not mixed silently.

See:
- `docs/SCENE_SEARCH.md`
- `docs/COG_ACCESS.md`
- `docs/SENTINEL2_INDICES.md`
- `docs/TEMPORAL_COMPOSITES.md`
- `examples/search_sentinel2.py`
- `examples/analyze_sentinel2.py`
- `examples/build_monthly_composites.py`
- `docs/satellite-data/sentinel-2-l2a.md`

## Interfaces

The **core is not tied to MCP or QGIS**. Both are adapters.

```text
Human / AI
   ├─ Python API
   ├─ CLI
   ├─ MCP server
   └─ QGIS adapter
          ↓
       eo2stats core
```

Candidate MCP tools:

- `list_datasets`
- `get_dataset_spec`
- `search_scenes`
- `inspect_scene`
- `build_composite`
- `compute_index`
- `extract_urban_features`
- `zonal_stats`
- `describe_indicator_support`
- `spatialize_indicator`
- `export_analysis_table`

## Existing open-source components to reuse

- `pystac-client` — STAC search
- `odc-stac` / `stackstac` — raster time-series loading
- `rasterio`, `rioxarray`, `xarray` — raster processing
- `geopandas`, `shapely` — vector processing
- `PySAL / tobler` — areal interpolation and dasymetric mapping
- `GeoAI` / `segment-geospatial` — remote-sensing feature extraction
- `OSMnx` and network libraries — road/network topology
- QGIS MCP projects — AI↔QGIS control layer rather than EO semantics

## First milestone status

Given an AOI and date range:

1. **search Sentinel-2 scenes — implemented**;
2. **report scene date/cloud/assets — implemented**;
3. **inspect raster scale/offset and read AOI COG windows — implemented**;
4. **calculate NDVI/NDWI/MNDWI/NDBI with versioned SCL QA — implemented**;
5. **aggregate scene results into fixed-grid monthly/seasonal composites — implemented**;
6. aggregate composites to a stable Master Analysis Grid;
7. attach static DEM-derived covariates;
8. export a provenance-aware long-format table.

The next processing milestone is Master Analysis Grid aggregation. Building/road/urban-form extraction and guarded spatialization remain separate modules so physical urban measurements are not confused with administrative-context variables.
