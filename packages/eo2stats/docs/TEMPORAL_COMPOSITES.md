# Temporal Composites

This document defines how scene-level EO index rasters become monthly, seasonal, or annual time-series composites in `eo2stats`.

## 1. Why this layer exists

A scene-level NDVI or NDBI raster is not yet a stable time-series observation. Different dates may have different cloud masks, raster windows, scene footprints, and valid-pixel counts.

The temporal layer therefore separates three operations:

```text
scene-level index rasters
        ↓
fixed output grid
        ↓
quality filtering + alignment
        ↓
period composite + n_observations
```

The resulting composite is still an EO raster. Aggregation to a 100 m or other Master Analysis Grid happens later.

## 2. Fixed output grid

All periods in one time-series call share one `CompositeGrid`.

The grid stores:
- CRS
- affine transform
- shape
- target GSD

The grid is derived once from the complete set of input observations and then reused for every month or season. This prevents a July raster and an August raster from having slightly different origins or extents simply because the source scene coverage differed.

If a study requires a pre-defined grid, callers can construct and pass a `CompositeGrid` explicitly.

## 3. Spatial support remains index-specific

Do not merge different index supports into one unlabeled raster grid.

Current Sentinel-2 defaults:

```text
NDVI  → 10 m
NDWI  → 10 m
MNDWI → 20 m
NDBI  → 20 m
```

A temporal composite accepts only one index and one target GSD at a time.

## 4. QA consistency

All scene-level observations in a composite must use the same versioned QA mask policy.

For example:

```text
research-clear-v1
```

and

```text
research-strict-v1
```

cannot be mixed silently in one period.

## 5. Scene-level quality threshold

`CompositePolicy.min_scene_valid_ratio` can remove a scene from a period when its AOI-level valid-pixel ratio is too low.

Example:

```python
CompositePolicy(
    method="median",
    min_scene_valid_ratio=0.30,
)
```

There is intentionally no universal built-in threshold. Appropriate values depend on climate, season, AOI size, observation frequency, and the research design.

Rejected scene IDs remain in provenance.

## 6. Per-pixel observation counts

The composite stores a separate `n_observations` raster.

This is a first-class output rather than a diagnostic to discard.

Example:

```text
pixel A: NDVI = 0.42, n_observations = 5
pixel B: NDVI = 0.39, n_observations = 1
```

The values should not automatically be interpreted as equal-quality observations.

`CompositePolicy.min_observations` allows a researcher to mask pixels that do not meet a selected temporal-support threshold.

Missing/cloudy observations are never replaced with zero.

## 7. Composite methods

Supported methods:
- `median`
- `mean`
- `percentile`

Median is the default because it is often more robust to residual cloud/shadow contamination and extreme scene values, but it is not declared universally superior.

Percentile example:

```python
CompositePolicy(method="percentile", percentile=75)
```

## 8. Resampling between scene grids

Scene-level rasters for the same index may not have exactly the same transform or CRS.

Before compositing, each continuous index raster is aligned to the fixed output grid.

Supported temporal alignment methods:
- `bilinear` (default)
- `nearest`

This resampling applies to an already-computed continuous spectral index, not to categorical SCL. SCL resampling is handled earlier in the scene-processing layer and remains nearest-neighbour only.

## 9. Time grouping

Grouping uses acquisition datetime, never file creation or download time.

### Monthly

```text
2026-08-03 → 2026-08
```

### Seasonal

Meteorological seasons:

```text
MAM: Mar–May
JJA: Jun–Aug
SON: Sep–Nov
DJF: Dec–Feb
```

December is assigned to the following season-year:

```text
2025-12 + 2026-01 + 2026-02 → 2026-DJF
```

### Annual

```text
2026-08-03 → 2026
```

For a custom date window, call `composite_observations(...)` directly and supply an explicit `period_key`.

## 10. Provenance

Each composite records:
- index
- period key
- CRS / transform / target GSD
- QA mask policy
- composite policy
- contributing item IDs
- contributing acquisition datetimes
- source collections
- rejected item IDs
- input / usable / rejected scene counts
- output valid-area ratio
- mean and maximum observation counts

## 11. Recommended research output

A later Master Analysis Grid step should preserve at least:

```text
spatial_id
period
index_name
value
valid_pixel_ratio
mean_n_observations
source_scene_count
mask_policy
composite_policy
source_support_m
```

This makes temporal support visible in panel and spatial-statistical analysis instead of hiding it behind a single index value.
