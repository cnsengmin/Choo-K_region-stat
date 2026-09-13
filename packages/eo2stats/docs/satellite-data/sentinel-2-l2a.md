---
dataset_id: sentinel-2-l2a
mission: Copernicus Sentinel-2
sensor: MSI
product: Level-2A Bottom-of-Atmosphere Surface Reflectance
processing_level: L2A
data_category: optical
spatial_resolution: 10m/20m/60m
temporal_role: dynamic
physical_unit: surface reflectance is unitless; QA layers vary
scale_factor: provider/product-baseline dependent
preferred_access: STAC + COG
preferred_format: COG
last_verified: 2026-09-13
---

# Sentinel-2 MSI Level-2A

## 1. Description

대기보정된 Bottom-of-Atmosphere surface reflectance와 Scene Classification(SCL) 등 품질·보조층을 제공하는 고해상도 광학제품이다. 도시·환경 시계열의 기본 광학자료로 사용한다.

## 2. Main uses

- NDVI / vegetation
- NDWI / MNDWI / water
- NDBI / built-up
- bare-soil / impervious proxies
- development/change detection
- seasonal vegetation dynamics

## 3. Spatial characteristics

- global systematic land/coastal observation
- orthorectified product using UTM/WGS84 tiling
- band resolutions: 10 m, 20 m, 60 m
- a study area may intersect multiple Sentinel-2 tiles

실제 사용 가능한 coverage는 사용 중인 STAC provider의 collection extent를 런타임에서 확인한다.

## 4. Temporal characteristics

Sentinel-2 계열은 2015년 이후 장기 시계열을 구성할 수 있다. 다만 L2A archive completeness와 reprocessing 범위는 provider에 따라 다를 수 있으므로 mission start date만으로 자료 존재를 가정하지 않는다.

Store:
- acquisition datetime
- platform
- tile
- processing baseline
- cloud metadata
- AOI valid-pixel ratio

## 5. Main bands

| Band | Meaning | Resolution |
|---|---|---:|
| B01 | Coastal aerosol | 60 m |
| B02 | Blue | 10 m |
| B03 | Green | 10 m |
| B04 | Red | 10 m |
| B05 | Red edge | 20 m |
| B06 | Red edge | 20 m |
| B07 | Red edge | 20 m |
| B08 | NIR | 10 m |
| B8A | Narrow NIR | 20 m |
| B09 | Water vapour | 60 m |
| B11 | SWIR | 20 m |
| B12 | SWIR | 20 m |
| SCL | Scene classification | 20 m |

B10 cirrus is not provided as an L2A BOA reflectance band.

## 6. Unit / scale / offset

Reflectance itself is dimensionless.

Do not blindly hard-code `DN / 10000` for every provider and processing baseline. Official SAFE products use quantification metadata, and Processing Baseline 04.00+ introduced band offset metadata to represent negative reflectance.

Preferred rule:

```text
1. inspect STAC raster metadata / product metadata
2. apply declared scale + offset
3. record the applied conversion in provenance
```

Earth Search currently exposes scale/offset in STAC raster metadata for its Sentinel-2 collections. The processing code should consume those declarations rather than infer a conversion only from the mission name.

## 7. QA

SCL includes classes for nodata, saturated/defective pixels, cloud shadows, vegetation, bare soil, water, cloud probability classes, cirrus and snow/ice.

For research composites, calculate **AOI-level valid pixel fraction** in addition to scene-level cloud-cover metadata.

## 8. Common indices

```text
NDVI  = (B08 - B04) / (B08 + B04)
NDWI  = (B03 - B08) / (B03 + B08)
MNDWI = (B03 - B11) / (B03 + B11)
NDBI  = (B11 - B08) / (B11 + B08)
```

B11 is native 20 m, so mixing it with 10 m bands requires an explicit resampling or target-support strategy.

## 9. Time-series rules

1. Keep product level consistent where possible.
2. Apply the same QA logic across dates.
3. Store number of usable observations per composite.
4. Do not treat cloudy months with few valid pixels as equal-quality observations.
5. Record processing baseline changes.
6. Prefer aggregation to a research support over pretending all mixed-resolution bands are natively 10 m.
7. Treat provider-side collection changes as provenance, not as automatic scientific discontinuities; verify the processing change before interpreting it as a temporal signal.

## 10. External integration

Typical static/quasi-static covariates:
- Copernicus DEM → elevation/slope/aspect
- buildings → footprint coverage/density
- road network → density/topology/accessibility
- zoning → geometric share/context
- population → direct grid or explicitly disaggregated estimate
- weather → temperature/precipitation

## 11. Access

Preferred discovery routes:
- Earth Search STAC
- Copernicus Data Space Ecosystem STAC

### Earth Search current collection mapping

As verified on 2026-09-13, Earth Search v1 represents Sentinel-2 L2A using two Collection-1-related collections:

```text
sentinel-2-pre-c1-l2a
sentinel-2-c1-l2a
```

`eo2stats` therefore keeps `sentinel-2-l2a` as a **logical dataset ID** and searches both provider collections when needed. Research scripts should not hard-code only one provider collection for a long time series.

Search fields:
- intersects/bbox
- datetime
- collection
- cloud cover
- platform

## 12. Official documentation

- https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html
- https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L2A.html
- https://earth-search.aws.element84.com/v1/collections
