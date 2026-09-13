# Indicator Spatialization Policy

## 1. Why this policy exists

Urban and social indicators do not all behave like satellite pixels.

A value can be:

- directly observed at a pixel;
- measured for a building or parcel;
- calculated from geometry;
- legally assigned to a zoning polygon;
- counted for an administrative area;
- estimated for a smaller area using a model.

Converting all of these to the same grid without recording their original support creates **false spatial precision** and can amplify ecological fallacy and the modifiable areal unit problem (MAUP).

`eo2stats` therefore treats spatialization as a documented transformation, not a harmless join.

## 2. Required metadata for every indicator

Each indicator must declare at least:

```yaml
indicator_id: fiscal_self_reliance_ratio
native_support_type: administrative_polygon
native_support_level: sigungu
quantity_type: intensive
measurement_type: ratio
observed_or_estimated: observed
redistribution_policy: contextual_only
mass_preserving: false
source_vintage: 2025
```

Recommended fields:

```yaml
temporal_support: annual
source_geometry_id: sigungu_2025
uncertainty_field: null
allowed_target_supports:
  - sigungu
  - grid_as_context
forbidden_operations:
  - area_weighted_disaggregation
```

## 3. Variable classes

### A. Directly observed raster

Examples:
- Sentinel-2 reflectance
- Landsat surface temperature
- DEM
- gridded weather products

Allowed:
- resampling with explicit method
- zonal statistics
- temporal compositing

Must retain:
- native resolution
- source CRS
- acquisition/validity time
- scale/offset
- resampling method

### B. Object or geometry-derived variable

Examples:
- building footprint
- building area
- road centerline
- parcel
- block
- water polygon
- AI segmentation result

Derived indicators can legitimately be calculated at a target support if the operation itself is defined there.

Examples:

```text
100m grid building coverage = building footprint area inside grid / grid area
100m road density = road length inside grid / grid area
block compactness = function(block geometry)
intersection density = intersections / analysis area
```

These are **new derived measurements**, not disaggregated administrative values.

### C. Regulatory / legal boundary attribute

Examples:
- zoning
- land-use zone
- district-unit plan
- protected area
- school district

These should normally be transferred by **geometric intersection**, not interpolation.

For a grid cell, suitable outputs include:

```text
zoning_dominant
zoning_share_residential
zoning_share_commercial
zoning_entropy
```

A boundary edge can cross a cell; forcing a single category without storing the share loses information.

### D. Administrative contextual indicator

Examples:
- fiscal self-reliance ratio
- municipal debt ratio
- welfare expenditure ratio
- local policy score
- mayoral/policy regime attribute

Default rule:

> Do not claim that the value exists at 100 m just because it is copied to 100 m rows.

It may be joined to grid rows for modelling, but metadata must preserve:

```text
value_support = sigungu
analysis_support = 100m_grid
spatialization_method = contextual_join
```

All child cells inherit the same contextual value. This is useful for multilevel/panel models, but it does not create within-municipality variation.

### E. Extensive count or total

Examples:
- population count
- number of firms
- total employment
- household count

These may be disaggregated **only when the method is explicit and mass preserving**.

Possible methods:

1. area-weighted interpolation;
2. binary dasymetric mapping;
3. weighted dasymetric mapping;
4. model-based small-area estimation.

Required validation:

```text
sum(target estimates within source polygon) ≈ source total
```

The output variable name must indicate estimation when appropriate, e.g.:

```text
population_est_100m
firms_est_250m
```

### F. Intensive rate / ratio / mean

Examples:
- fiscal ratio
- unemployment rate
- average income
- average age

These must **not** be redistributed like totals.

Area weighting an intensive ratio is usually meaningless unless the underlying numerator and denominator are separately available and spatialized.

Preferred approach:

```text
spatialize numerator
spatialize denominator
recompute rate at target support
```

Otherwise preserve as contextual source-level information.

### G. Model-derived small-area estimate

Examples:
- population disaggregation using buildings, roads and land cover
- building-height estimate from imagery
- impervious surface probability
- land-use classification probability

Must record:
- model name/version
- input covariates
- training geography if known
- prediction date
- uncertainty/confidence if available
- conservation constraint if applicable

## 4. Spatialization decision tree

```text
Does the variable naturally exist at target support?
 ├─ yes → calculate/aggregate at target support
 └─ no
     ↓
Is it a legal/regulatory polygon attribute?
 ├─ yes → geometric intersection / share
 └─ no
     ↓
Is it an extensive total?
 ├─ yes → explicit mass-preserving disaggregation may be allowed
 └─ no
     ↓
Is it an intensive/rate/context variable?
 ├─ yes → contextual join only, unless numerator+denominator permit reconstruction
 └─ no → require method review
```

## 5. Disaggregation methods

### Area weighted

Assumes uniform distribution over source polygon area.

Pros:
- simple
- transparent

Cons:
- often unrealistic in urban space
- sensitive to MAUP
- allocates values to parks, water, industrial land, mountains unless constrained

### Dasymetric

Uses ancillary information to define plausible allocation space or weights.

Possible ancillary layers:
- buildings
- built-up area
- land cover
- night lights
- roads
- POIs
- satellite-derived settlement

This is preferred when the target concept has a plausible spatial relationship with those covariates.

### Model based

Learns a relationship between source-level totals/density and higher-resolution covariates, then predicts a weighting surface.

It can improve spatial detail but the output remains an **estimate**, not direct observation.

## 6. Urban / architectural indicators as the distinctive layer

The most promising project contribution is not arbitrary downscaling of municipal statistics. It is generating new small-area indicators from high-resolution physical evidence.

Candidate families:

### Built form
- building coverage ratio
- building count density
- mean/median footprint area
- footprint compactness
- building orientation
- inter-building spacing
- building-height statistics when height is available
- estimated floor-area density only when vertical information is defensible

### Street / topology
- road density
- intersection density
- node degree
- block area
- block perimeter
- circuity
- connected component metrics
- pedestrian-network accessibility

### Land surface
- vegetation share
- impervious/built-up share
- water share
- bare-soil share
- land-cover entropy
- surface temperature

### Morphological context
- built-up fragmentation
- edge density
- texture/heterogeneity
- green-building adjacency
- road-building relationship

These indicators can be measured on grids, blocks, parcels, buffers or neighborhoods because their derivation is defined from fine-scale geometry/raster evidence.

## 7. Relationship to open-source tools

Reuse rather than reimplement:

- PySAL `tobler`: areal interpolation, dasymetric mapping, change of support
- WorldPop methodology: model-based dasymetric redistribution for population
- GeoAI / segment-geospatial: segmentation and raster-to-vector feature extraction
- OSMnx: street topology/network metrics
- QGIS Processing: desktop GIS operations

`eo2stats` adds the **semantic contract** telling these tools when a transformation is conceptually valid and how the result must be labelled.

## 8. Output provenance example

```yaml
indicator_id: population_est_100m
value: 87.4
analysis_support: grid_100m
native_support: sigungu
transformation: random_forest_dasymetric
mass_preserving: true
ancillary_data:
  - building_coverage
  - road_distance
  - sentinel2_builtup
source_total: 153244
uncertainty: null
```

For fiscal context:

```yaml
indicator_id: fiscal_self_reliance_ratio
value: 42.1
analysis_support: grid_100m
native_support: sigungu
transformation: contextual_join
estimated_at_grid: false
```

That difference must remain visible in every downstream export.