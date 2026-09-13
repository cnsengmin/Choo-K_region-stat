# MCP Adapter Design

## 1. Principle

MCP is an interface to `eo2stats`, not the scientific core.

The core must remain callable from Python, CLI, notebooks, QGIS and batch workflows without requiring an MCP client.

## 2. Why MCP is useful here

EO/GIS workflows contain repeated research actions that are easier to express semantically than as raw file operations:

```text
"Find cloud-light Sentinel-2 observations over this AOI in May 2024"
"Explain whether this fiscal indicator can be converted to a 100 m grid"
"Generate building-coverage statistics for these grid cells"
"Create a monthly NDVI panel and attach DEM covariates"
```

An MCP layer can expose those high-level actions while returning provenance and warnings.

## 3. Proposed resources

```text
eo2stats://datasets
eo2stats://datasets/{dataset_id}
eo2stats://indicators
eo2stats://indicators/{indicator_id}
eo2stats://policies/spatialization
eo2stats://runs/{run_id}
```

Dataset resources are generated from `docs/satellite-data/*.md` or a future synchronized YAML registry.

## 4. Proposed tools

### Catalog / discovery

- `list_datasets`
- `get_dataset_spec`
- `search_scenes`
- `inspect_scene`

### EO processing

- `build_composite`
- `compute_index`
- `zonal_stats`
- `derive_terrain`

### Urban features

- `extract_objects`
- `calculate_building_metrics`
- `calculate_network_metrics`
- `calculate_landscape_metrics`

### Indicator semantics

- `describe_indicator_support`
- `check_spatialization`
- `spatialize_indicator`

### Outputs

- `export_analysis_table`
- `export_geoparquet`
- `get_provenance`

## 5. Tool behavior requirement

A tool must not silently perform a conceptually invalid change of support.

Example request:

```text
spatialize fiscal_self_reliance_ratio from sigungu to 100m grid
```

Expected response behavior:

```text
method requested: area_weighted
status: rejected
reason: source is an intensive administrative ratio, not an additive total
alternatives:
  - contextual_join
  - provide numerator + denominator and recompute after defensible spatialization
```

## 6. QGIS MCP interoperability

Existing QGIS MCP projects can control the desktop application and execute QGIS Processing tools.

Recommended division:

```text
eo2stats MCP
  - source semantics
  - EO retrieval
  - scientific transformation
  - support/provenance policy

QGIS MCP
  - desktop project control
  - layer management
  - styling/rendering
  - generic Processing Toolbox operations
```

Outputs from eo2stats should use common GIS formats so an AI agent can hand them to QGIS without a custom bridge.

## 7. Safety and reproducibility

Prefer named, parameterized operations over arbitrary Python execution.

Each processing tool should return:
- operation name/version
- parameters
- input dataset IDs
- source item IDs
- output path/reference
- spatial support
- temporal support
- warnings
- quality/uncertainty metadata

## 8. First MCP milestone

Do not begin with every GIS operation.

Implement only:

```text
list_datasets
get_dataset_spec
search_scenes
check_spatialization
```

These four tools validate the project's two central ideas:
1. low-friction access to open EO data;
2. explicit semantics for spatial support.

Processing tools should be added after the underlying Python functions are stable.