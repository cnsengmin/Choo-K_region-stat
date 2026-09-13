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
last_verified: 2026-09-14
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

As verified on 2026-09-14, Earth Search `sentinel-2-c1-l2a` declares reflectance assets with STAC raster metadata such as:

```text
scale  = 0.0001
offset = -0.1
```

This is a provider/product declaration, not a mission-wide constant that should be copied into all processing code. `eo2stats` consumes the asset metadata instead of inferring the conversion only from the mission name.

## 7. Scene Classification / QA

SCL is a 20 m categorical layer.

| SCL | Meaning |
|---:|---|
| 0 | No data |
| 1 | Saturated / defective |
| 2 | Dark area pixels |
| 3 | Cloud shadows |
| 4 | Vegetation |
| 5 | Bare soils |
| 6 | Water |
| 7 | Low cloud probability / unclassified |
| 8 | Medium cloud probability |
| 9 | High cloud probability |
| 10 | Thin cirrus |
| 11 | Snow / ice |

The default `eo2stats` policy is `research-clear-v1`:

```text
invalid = 0, 1, 3, 7, 8, 9, 10, 11
```

A stricter policy also excludes class 2. A Copernicus-mosaic-like policy is available separately.

SCL is always aligned with nearest-neighbour resampling. It is not a continuous land-cover variable and must not be interpolated with bilinear or cubic methods.

For research composites, calculate **AOI-level valid pixel fraction** in addition to scene-level cloud-cover metadata.

See `../SENTINEL2_INDICES.md`.

## 8. Common indices and output support

```text
NDVI  = (B08 - B04) / (B08 + B04) → 10 m target grid
NDWI  = (B03 - B08) / (B03 + B08) → 10 m target grid
MNDWI = (B03 - B11) / (B03 + B11) → 20 m target grid
NDBI  = (B11 - B08) / (B11 + B08) → 20 m target grid
```

B11 is native 20 m. `eo2stats` therefore downsamples the 10 m companion band to the 20 m SWIR grid for MNDWI/NDBI rather than upsampling SWIR and calling the result native 10 m information.

## 9. Time-series rules

1. Keep product level consistent where possible.
2. Apply the same versioned QA logic across dates.
3. Store number of usable observations per composite.
4. Do not treat cloudy months with few valid pixels as equal-quality observations.
5. Record processing baseline changes.
6. Prefer aggregation to a research support over pretending all mixed-resolution bands are natively 10 m.
7. Treat provider-side collection changes as provenance, not as automatic scientific discontinuities; verify the processing change before interpreting it as a temporal signal.
8. Retain `valid_pixel_ratio`, `masked_pixel_ratio` and `n_valid_pixels` for every scene-derived result.

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

As verified in September 2026, Earth Search v1 represents Sentinel-2 L2A using two Collection-1-related collections:

```text
sentinel-2-pre-c1-l2a
sentinel-2-c1-l2a
```

`eo2stats` therefore keeps `sentinel-2-l2a` as a **logical dataset ID** and searches both provider collections when needed. Research scripts should not hard-code only one provider collection for a long time series.

Current Collection-1 analytical asset keys include:

```text
red
green
blue
nir
nir08
swir16
swir22
scl
cloud
snow
aot
```

Search fields:
- intersects/bbox
- datetime
- collection
- cloud cover
- platform

## 12. Official / provider documentation

- https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html
- https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L2A.html
- https://documentation.dataspace.copernicus.eu/Data/Others/Sentinel2_Mosaic_Algorithm.html
- https://earth-search.aws.element84.com/v1/collections/sentinel-2-c1-l2a
