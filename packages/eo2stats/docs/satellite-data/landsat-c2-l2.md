---
dataset_id: landsat-c2-l2
mission: Landsat
sensor: OLI/OLI-2 + TIRS/TIRS-2
product: Collection 2 Level-2 Surface Reflectance and Surface Temperature
processing_level: L2
data_category: optical+thermal
spatial_resolution: 30m analysis grid for SR/ST products
temporal_role: dynamic
physical_unit: SR unitless; ST Kelvin after scaling
scale_factor: SR 0.0000275; ST 0.00341802
offset: SR -0.2; ST +149.0
preferred_access: STAC + cloud assets
preferred_format: COG where available
last_verified: 2026-09-13
---

# Landsat Collection 2 Level-2

## 1. Description

장기적인 surface reflectance와 surface temperature 시계열을 구축하기 좋은 USGS 분석용 제품이다. Sentinel-2보다 공간해상도는 낮지만 긴 archive와 열환경 분석에 강점이 있다.

## 2. Main uses

- long-term urban expansion
- vegetation/water/built-up change
- NDVI/NDBI and spectral indices
- land surface temperature
- pre-Sentinel-2 historical analysis

## 3. Main Landsat 8/9 variables

| Asset | Meaning | Resolution |
|---|---|---:|
| SR_B1 | Coastal aerosol | 30 m |
| SR_B2 | Blue | 30 m |
| SR_B3 | Green | 30 m |
| SR_B4 | Red | 30 m |
| SR_B5 | NIR | 30 m |
| SR_B6 | SWIR1 | 30 m |
| SR_B7 | SWIR2 | 30 m |
| ST_B10 | Surface temperature | distributed on 30 m grid |
| QA_PIXEL | cloud/shadow/snow bit QA | 30 m |
| QA_RADSAT | radiometric saturation QA | 30 m |

## 4. Surface Reflectance scaling

```text
SR = DN × 0.0000275 - 0.2
```

- physical quantity: surface reflectance
- unit: dimensionless
- Collection 2 scaling must not be mixed with older Collection 1 conventions.

## 5. Surface Temperature scaling

```text
ST_K = DN × 0.00341802 + 149.0
ST_C = ST_K - 273.15
```

The native science-product unit after scaling is Kelvin. Store whether a downstream table was converted to Celsius.

## 6. QA

At minimum inspect:
- `QA_PIXEL`
- `QA_RADSAT`
- aerosol QA where relevant

Cloud, cloud shadow, snow and saturated pixels should be masked according to a documented rule.

## 7. Time-series rules

1. Keep Collection and processing level consistent.
2. Record sensor/platform generation.
3. Never replace missing ST with zero or an unconditional mean.
4. Store acquisition date and available geometry/quality metadata.
5. For urban heat studies, consider weather and acquisition-time context.
6. When combining Landsat generations, retain sensor identity even after harmonization.

## 8. Role with Sentinel-2

- Sentinel-2: finer urban spatial detail
- Landsat: longer time series + thermal information
- HLS: 30 m harmonized Landsat/Sentinel time series

Do not assume two sensors produce identical values simply because the derived indicator has the same name.

## 9. Official documentation

- https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products
- https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products
