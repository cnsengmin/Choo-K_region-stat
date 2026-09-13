---
dataset_id: hls-v2
mission: NASA Harmonized Landsat Sentinel-2
sensor: OLI/OLI-2 + MSI
product: HLSL30.002 / HLSS30.002
processing_level: harmonized surface reflectance
data_category: optical
spatial_resolution: 30m
temporal_role: dynamic
physical_unit: reflectance unitless
scale_factor: 0.0001
offset: 0
preferred_access: NASA Earthdata / cloud assets
preferred_format: COG
last_verified: 2026-09-13
---

# Harmonized Landsat Sentinel-2 (HLS) Version 2

## 1. Description

Landsat과 Sentinel-2 surface reflectance를 30 m 공통격자와 조화처리로 연결해 장기·고빈도 광학 시계열을 만들기 위한 NASA 제품이다.

## 2. Components

- `HLSL30`: Landsat-derived 30 m product
- `HLSS30`: Sentinel-2-derived 30 m product

HLS is useful when temporal density and cross-sensor consistency matter more than preserving Sentinel-2's native 10 m spatial detail.

## 3. Values

Version 2 reflectance layers are stored as scaled integers in the standard product representation.

```text
reflectance = DN * 0.0001
```

- physical quantity: reflectance
- unit: dimensionless
- standard offset: 0
- fill values must be handled explicitly

Always inspect asset metadata because metadata issues can occur in particular granules/providers; the pipeline should warn when expected scale/offset metadata is absent rather than silently guessing.

## 4. Research role

Best suited for:
- long multi-sensor optical series
- monthly/seasonal composites
- reducing gaps between Landsat and Sentinel acquisition opportunities
- analyses where a 30 m common support is acceptable

Prefer native Sentinel-2 L2A when within-city fine spatial differentiation at 10 m is the primary objective.

## 5. Time-series cautions

Harmonization reduces but does not eliminate every observational difference. Retain:
- source mission/product (`L30` or `S30`)
- acquisition date
- QA layer information
- valid-pixel fraction
- composite observation count

## 6. Official documentation

- https://lpdaac.usgs.gov/documents/1698/HLS_User_Guide_V2.pdf
- https://doi.org/10.5067/HLS/HLSL30.002
- https://doi.org/10.5067/HLS/HLSS30.002
