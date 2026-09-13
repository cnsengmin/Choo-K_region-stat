# Urban & Architectural Feature Registry

## 1. Purpose

This document defines candidate small-area urban/architectural indicators and, crucially, the evidence required to calculate them.

The goal is not to maximize the number of indicators. It is to distinguish:

```text
measured from fine-scale physical evidence
vs
estimated with an explicit model
vs
administrative context attached to the area
```

## 2. Evidence hierarchy

### Tier A — Direct geometry / authoritative object data

Examples:
- cadastral parcel
- building footprint
- building registry height/floors
- road centerline
- zoning polygon

Preferred when complete and temporally compatible.

### Tier B — EO-derived physical observation

Examples:
- spectral index
- land-surface temperature
- DEM
- built-up/vegetation/water surface

These can generate real small-area variation at the raster's support.

### Tier C — AI-derived object/attribute

Examples:
- segmented building footprint
- road probability/vector
- estimated building height
- land-use classification

Treat as estimates and retain model/confidence/vintage.

### Tier D — Administrative/contextual statistic

Examples:
- fiscal health
- municipal expenditure
- policy score
- administrative-level demographic ratio

Useful in multilevel urban analysis, but not a source of genuine within-unit spatial detail unless supported by an explicit small-area model.

## 3. Built-form indicators

| Indicator | Preferred input | Valid target support | Notes |
|---|---|---|---|
| building coverage ratio | building polygons | grid/block/parcel | footprint area ÷ target area |
| building count density | building polygons | grid/block | count per area |
| mean footprint area | building polygons | grid/block | define centroid vs intersect rule |
| footprint compactness | building polygons | building then aggregate | preserve building-level distribution |
| building orientation | building polygons | building then circular aggregate | use circular statistics |
| inter-building spacing | footprints/centroids | neighborhood/grid | method must be documented |
| height mean/max | registry/LiDAR/DSM/model | grid/block | source quality is critical |
| floor-area density | footprint + defensible floors/height | grid/block | do not infer FAR from footprint alone |
| vertical heterogeneity | height distribution | grid/block | requires reliable vertical data |

## 4. Street and topology indicators

| Indicator | Input | Notes |
|---|---|---|
| road length density | road centerlines | length / area |
| intersection density | routable network | node-definition rule required |
| mean node degree | graph | topology-sensitive |
| circuity | graph + geometry | network definition required |
| block size | planarized street/block geometry | treatment of expressways/rivers matters |
| block compactness | block polygons | multiple formulas possible |
| centrality | network graph | metric and radius must be explicit |
| accessibility | network + destinations | travel mode/cost/time required |

Candidate engine: OSMnx/networkx or authoritative Korean road data adapters.

## 5. Land-surface / environmental indicators

Possible sources: Sentinel-2, Landsat, Sentinel-1, DEM, weather products.

Candidate variables:
- NDVI / vegetation condition
- vegetation fraction
- water fraction
- built-up / impervious proxy
- surface temperature
- terrain elevation/slope/aspect
- moisture/backscatter metrics
- seasonal variability
- change magnitude

A spectral index is not automatically equivalent to a semantic land-use category.

## 6. Morphological indicators

Derived after raster/vector normalization:

- patch count/density
- edge density
- fragmentation
- connectivity
- adjacency matrix
- land-cover entropy
- building-road proximity
- green-building interface
- built-up continuity
- texture/heterogeneity

These metrics need explicit neighborhood/window definitions.

## 7. Regulatory and planning indicators

Examples:
- zoning share
- dominant zoning
- mixed-zoning entropy
- planning-district coverage
- height-control district coverage
- development-restriction coverage

Method:

```text
source legal polygon × target geometry → overlap/share
```

Do not interpolate legal categories across boundaries.

## 8. Social / administrative context

Examples:
- fiscal self-reliance
- debt ratio
- welfare expenditure
- local tax base
- policy/program presence

Default behavior:

```text
attach as contextual variable
retain native administrative support
never claim within-unit variation
```

If a researcher requests spatial disaggregation, the system should ask/record:
- Is the quantity additive?
- What mechanism links the indicator to fine-scale covariates?
- Is there validation data?
- Is conservation required?
- Is the result labelled as an estimate?

## 9. Time-series implications

Urban form is not uniformly time varying.

Classify each feature:

```text
dynamic:        NDVI, LST, surface water, construction change
quasi-static:   buildings, roads, land use, zoning
static:         terrain for most urban studies
contextual:     annual fiscal/policy indicators
```

Do not reuse a 2026 building layer as though it represented 2015 without recording the vintage mismatch.

## 10. Minimum output metadata

Every indicator output should include or be traceable to:

```yaml
indicator_id:
value:
unit:
native_support:
analysis_support:
evidence_type:
source_dataset:
source_vintage:
transformation:
model_version:
quality_or_uncertainty:
```

## 11. Near-term implementation priorities

1. building coverage/count/footprint distribution
2. road length/intersection/block metrics
3. Sentinel-2 vegetation/water/built-up indicators
4. Landsat surface temperature
5. DEM terrain variables
6. zoning share/mix by geometry
7. multi-temporal building/built-up change
8. AI-derived footprints where authoritative geometry is absent or historical reconstruction is needed

The project should prefer authoritative vector data for present-day Korean urban form when it is available, and use imagery/AI where it adds temporal coverage, missing geometry, independent validation, or genuinely new observations.