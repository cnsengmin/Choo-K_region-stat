---
dataset_id: sentinel-1-grd
mission: Copernicus Sentinel-1
sensor: C-band SAR
product: Level-1 GRD / provider-processed RTC
processing_level: L1 GRD or derived RTC
data_category: sar
spatial_resolution: mode/product dependent; IW commonly ~10m-class spacing
temporal_role: dynamic
physical_unit: raw GRD detected amplitude; calibrated backscatter commonly linear power or dB
scale_factor: do not hardcode
offset: do not hardcode
preferred_access: STAC; prefer analysis-ready RTC when available
preferred_format: COG where available
last_verified: 2026-09-13
---

# Sentinel-1 GRD / RTC

## 1. Description

구름과 일조조건의 영향을 광학영상보다 덜 받는 C-band SAR 자료다. 다만 GRD 저장값 자체와 분석용 backscatter를 구분해야 하며 calibration/terrain correction 조건이 시계열 비교에 중요하다.

## 2. GRD value meaning

Official GRD products are detected, multi-looked Level-1 SAR products projected to ground range. Phase information is not retained in GRD.

Calibration metadata can be used to derive backscatter coefficients such as beta0, sigma0 or gamma0.

A conceptual calibration relation is:

```text
calibrated_power(i) = |DN_i|^2 / A_i^2
```

where `A_i` comes from the relevant calibration lookup table.

## 3. Analysis values

Provider-processed products may expose:
- sigma0
- gamma0
- terrain-corrected gamma0

When linear power is transformed to decibels:

```text
dB = 10 * log10(linear_power)
```

The variable name and provenance must state whether the value is linear or dB.

## 4. Polarization and orbit

Common polarizations include VV, VH, HH and HV. Always inspect item metadata.

For time-series analysis record:
- acquisition mode
- polarization
- orbit direction
- relative orbit
- incidence/geometry metadata when available

Ascending and descending acquisitions should not be blindly averaged into one homogeneous series.

## 5. DEM relationship

DEM can be used in SAR orthorectification/radiometric terrain correction. This is conceptually separate from later using elevation/slope as explanatory variables.

Record both:

```text
processing_dem = Copernicus DEM / other
analysis_covariate = elevation_mean / slope_mean / ...
```

## 6. Recommended project strategy

Initial implementation should prefer an analysis-ready RTC product/provider path where practical. Direct GRD calibration and terrain correction can be added as an advanced adapter.

Store:
- backscatter coefficient definition
- RTC yes/no
- DEM used for correction
- speckle-filter settings
- linear/dB
- orbit/polarization

## 7. Official documentation

- https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel1.html
- https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S1GRD.html
