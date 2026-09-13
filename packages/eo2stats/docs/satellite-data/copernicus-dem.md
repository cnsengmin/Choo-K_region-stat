---
dataset_id: cop-dem-glo-30
mission: Copernicus DEM
sensor: derived elevation model
product: GLO-30
processing_level: derived DEM
data_category: dem
spatial_resolution: 1 arc-second class (~30m)
temporal_role: static
physical_unit: meter
scale_factor: 1
offset: 0
preferred_access: STAC/COG when provider offers it
preferred_format: GeoTIFF/COG
last_verified: 2026-09-13
---

# Copernicus DEM GLO-30

## 1. Description

전세계 고도와 지형조건을 제공하는 DEM이다. 위성 시계열에서는 주로 **시간불변 또는 준고정 공변량**으로 사용하고, Sentinel-1 terrain processing에도 활용할 수 있다.

## 2. Core characteristics

- GLO-30: approximately 30 m-class horizontal spacing
- vertical unit: metre
- horizontal reference: WGS84 family
- vertical reference documented by Copernicus DEM as EGM2008
- distributed as GeoTIFF products

## 3. Recommended derived covariates

Calculate terrain derivatives once and store them separately from dynamic observations.

Possible variables:
- elevation_mean/min/max/sd
- slope_mean/sd
- aspect_sin / aspect_cos
- terrain ruggedness
- topographic position
- relative elevation

Aspect should not generally be averaged as a simple degree value across the 0/360 boundary; circular encodings are preferred.

## 4. Master-support integration

For a 100 m analysis grid, terrain derivatives should preferably be calculated on the native DEM first and then summarized to the target grid.

```text
grid_id | elevation_mean | elevation_sd | slope_mean | aspect_sin | aspect_cos
```

## 5. Time-series role

Default data model:

```text
dynamic_observations: spatial_id × datetime
static_covariates: spatial_id
```

Do not duplicate unchanged DEM fields for every satellite date unless a downstream format requires a flattened table.

Large earthworks, reclamation, mining or construction can make terrain time-varying; such studies require date-aware elevation products instead of treating DEM as permanently static.

## 6. Sentinel-1 processing

If Copernicus DEM is used for SAR terrain correction, distinguish:

```text
processing provenance: DEM used to correct SAR geometry/backscatter
analysis covariate: elevation/slope used in the statistical model
```

## 7. Official documentation

- https://dataspace.copernicus.eu/explore-data/data-collections/copernicus-contributing-missions/collections-description/COP-DEM
