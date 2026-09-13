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

## Current executable milestone: STAC scene discovery

The first working EO API is now implemented for scene discovery.

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

rows = [scene.to_dict() for scene in scenes]
```

The public logical dataset ID is intentionally separated from provider-specific collection IDs. For example, current Earth Search Sentinel-2 L2A discovery resolves `sentinel-2-l2a` across both pre-Collection-1 and Collection-1 catalogs when necessary for long time series.

See:
- `docs/SCENE_SEARCH.md`
- `examples/search_sentinel2.py`
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

## First milestone

Given an AOI and date range:

1. **search Sentinel-2 scenes — implemented**;
2. **report scene date/cloud/assets — implemented**;
3. read only AOI COG windows;
4. calculate NDVI/NDBI/NDWI with documented QA;
5. aggregate to a stable analysis grid;
6. attach static DEM-derived covariates;
7. export a provenance-aware long-format table.

The next milestone adds COG window reading and scale/offset inspection. Building/road/urban-form extraction and the guarded spatialization layer remain separate modules so physical urban measurements are not confused with administrative-context variables.
