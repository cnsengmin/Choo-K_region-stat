# Architecture

## 1. Design goal

`eo2stats` connects open Earth observation data to urban research without erasing differences in spatial meaning.

The architecture separates three problems that are often mixed together:

```text
A. OBSERVE
Satellite / DEM / weather / imagery
        ↓
B. EXTRACT
physical urban objects and measurable form
        ↓
C. SPATIALIZE
administrative/social indicators with explicit change-of-support rules
```

## 2. Layer A — Observation

Purpose: retrieve and standardize remotely sensed/environmental observations.

Components:

```text
catalog/
providers/
readers/
quality/
composites/
```

Expected technologies:
- STAC / pystac-client
- Earth Search / Copernicus Data Space / NASA providers
- odc-stac or stackstac
- rasterio / xarray / rioxarray

Outputs retain:
- collection/item/asset IDs
- acquisition datetime
- native spatial resolution
- CRS
- unit
- scale/offset
- QA rule
- valid-pixel fraction

## 3. Layer B — Urban Feature Extraction

Purpose: turn fine spatial evidence into **new physical urban measurements**.

This is expected to be the most distinctive layer for urban/architectural research.

### 3.1 Raster-derived surfaces

Examples:
- vegetation/water/built-up indices
- surface temperature
- imperviousness
- texture
- change metrics

### 3.2 Object extraction

Adapters may call mature GeoAI projects/models to extract:
- building footprints
- roads
- water
- vegetation
- solar panels
- land-cover objects

Outputs must include model provenance and confidence when available.

### 3.3 Geometry and topology

After vectorization, calculate urban-form indicators rather than stopping at segmentation.

Buildings:
- coverage ratio
- count density
- footprint size distribution
- compactness
- orientation
- spacing
- height statistics when a defensible height source exists

Streets/networks:
- length density
- node/intersection density
- degree
- circuity
- connectedness
- centrality

Blocks/parcels:
- block size
- perimeter
- compactness
- frontage-related measures where inputs permit

Landscape/morphology:
- fragmentation
- edge density
- adjacency
- heterogeneity
- land-cover entropy

Candidate reusable tools:
- GeoAI / segment-geospatial for imagery→objects
- OSMnx/networkx for street topology
- shapely/geopandas for geometry metrics
- PySAL ecosystem for spatial statistics

## 4. Layer C — Indicator Spatialization

Purpose: reconcile variables whose native support is larger or conceptually different from the target analysis unit.

This layer is **guarded**.

### 4.1 Never confuse row resolution with information resolution

If a sigungu fiscal ratio is joined onto 10,000 grid rows:

```text
row support = grid
information support = sigungu
```

The value remains a sigungu-level contextual variable.

### 4.2 Regulatory polygons are geometry, not interpolation

Zoning and similar legal boundaries should be intersected with the target unit.

Possible outputs:
- dominant class
- share by class
- boundary-crossing flag
- entropy/mix

### 4.3 Counts can be estimated only under an explicit redistribution model

Population or establishment totals may use:
- area weighting
- dasymetric constraints
- weighted dasymetric surfaces
- model-based small-area estimation

The transformation must preserve the source total when conservation is required.

### 4.4 Rates remain contextual unless reconstructible

A ratio/mean should not be distributed as though it were a count.

When numerator and denominator exist separately, spatialize those components and recompute the target-scale rate.

See `INDICATOR_SPATIALIZATION.md`.

## 5. Spatial support model

Every variable carries two concepts:

```text
native_support
analysis_support
```

Example:

```yaml
indicator_id: building_coverage
native_support: building_polygon
analysis_support: grid_100m
transformation: polygon_area_fraction
```

versus:

```yaml
indicator_id: fiscal_self_reliance
native_support: sigungu
analysis_support: grid_100m
transformation: contextual_join
estimated_at_analysis_support: false
```

## 6. Core package vs adapters

```text
                 +------------------+
                 |    MCP server    |
                 +---------+--------+
                           |
+-----------+      +-------v-------+      +-------------+
| QGIS      +----->+ eo2stats core +<-----+ Python / CLI|
| adapter   |      +-------+-------+      +-------------+
+-----------+              |
                           v
               Parquet / GeoParquet / COG
```

The core contains scientific/data semantics. MCP and QGIS only expose capabilities.

This prevents an MCP-specific implementation from becoming the only way to use the project.

## 7. MCP responsibility

Good MCP tools are high-level and auditable:

```text
search_scenes
get_dataset_spec
compute_index
extract_urban_features
calculate_urban_form
spatialize_indicator
explain_spatialization
export_analysis_table
```

Avoid exposing only generic `execute_python` as the main interface. Generic code execution may remain optional, but reproducible named operations should be preferred.

## 8. QGIS relationship

Existing QGIS MCP projects already solve AI↔QGIS control: loading layers, executing Processing algorithms, rendering maps and running PyQGIS.

`eo2stats` should complement rather than duplicate that work.

Possible integration:

```text
AI
 ↓
eo2stats MCP ── produces documented layer/table
 ↓
QGIS MCP ────── loads, styles, inspects, edits and maps it
```

or a future QGIS plugin may call `eo2stats` directly.

## 9. Master analysis supports

Do not force a single permanent 100 m grid for every research question.

Supported target geometries should include:
- regular grid
- administrative units
- census units
- parcels
- buildings
- urban blocks
- custom buffers
- network catchments

A project configuration chooses one or more supports and records them.

## 10. Provenance first

Every output should be able to answer:

1. What source observation/statistic produced this value?
2. At what native spatial and temporal support was it measured?
3. Was it observed, geometrically derived, interpolated or model-estimated?
4. What transformation moved it to the analysis support?
5. What uncertainty or quality indicator is available?
6. Can the exact operation be rerun?