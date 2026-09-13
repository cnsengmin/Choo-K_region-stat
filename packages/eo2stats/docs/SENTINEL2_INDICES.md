# Sentinel-2 QA masking and spectral indices

This document defines the first reproducible Sentinel-2 analysis policy used by `eo2stats`.

The goal is not to force every band onto a 10 m grid. The goal is to preserve the information support of each source while producing comparable time-series observations.

## 1. Supported indices

| Index | Formula | Source bands | Output grid |
|---|---|---|---:|
| NDVI | `(nir - red) / (nir + red)` | B08 10 m + B04 10 m | 10 m |
| NDWI | `(green - nir) / (green + nir)` | B03 10 m + B08 10 m | 10 m |
| MNDWI | `(green - swir16) / (green + swir16)` | B03 10 m + B11 20 m | 20 m |
| NDBI | `(swir16 - nir) / (swir16 + nir)` | B11 20 m + B08 10 m | 20 m |

The mixed-resolution indices deliberately use the **20 m SWIR grid** as the target support. The 10 m source band is downsampled with average resampling. This avoids presenting a SWIR-dependent result as native 10 m information.

## 2. Scene Classification Layer

Sentinel-2 L2A SCL is a 20 m categorical product.

| Class | Meaning |
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

SCL is **never interpolated with bilinear or cubic resampling**. It is aligned to an index grid with nearest-neighbour only.

Official reference:
- https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L2A.html

## 3. Versioned mask policies

### `research-clear-v1` — default

Invalid:

```text
0, 1, 3, 7, 8, 9, 10, 11
```

Valid by default:

```text
2, 4, 5, 6
```

Rationale:
- class 2 is retained because dark-area pixels can represent real surfaces and are not automatically clouds;
- class 7 is excluded because it is uncertain/unclassified;
- snow/ice is excluded because it can create strong seasonal artefacts in general urban/environmental indices.

### `research-strict-v1`

Invalid:

```text
0, 1, 2, 3, 7, 8, 9, 10, 11
```

This is useful when dark-area pixels should also be discarded.

### `copernicus-mosaic-like-v1`

Invalid:

```text
0, 1, 3, 7, 8, 9, 10
```

This follows the invalid SCL classes used by the Copernicus Sentinel-2 mosaic algorithm, while explicitly treating class 0 as nodata. Snow/ice remains usable.

Reference:
- https://documentation.dataspace.copernicus.eu/Data/Others/Sentinel2_Mosaic_Algorithm.html

## 4. Resampling policy

### Categorical layers

```text
SCL → nearest-neighbour only
```

### Continuous reflectance

If a finer source is moved to a coarser target:

```text
10 m → 20 m : average
```

If continuous data must otherwise be aligned to a different grid:

```text
bilinear
```

The current default workflow avoids upsampling 20 m SWIR to manufacture 10 m NDBI/MNDWI.

## 5. Scale and offset

`eo2stats` reads scale/offset from STAC raster metadata through `AssetSpec`.

For the current Earth Search Sentinel-2 Collection-1 L2A collection, reflectance assets declare values such as:

```text
scale  = 0.0001
offset = -0.1
```

These values are provider/product metadata and are **not hard-coded into index formulas**.

The processing order is:

```text
COG DN
→ declared scale/offset
→ physical reflectance
→ grid alignment
→ SCL mask
→ spectral index
```

SCL is classification data and is not reflectance-scaled.

Current provider reference:
- https://earth-search.aws.element84.com/v1/collections/sentinel-2-c1-l2a

## 6. Quality statistics

Every index result stores:

```text
n_total_pixels
n_valid_pixels
valid_pixel_ratio
masked_pixel_ratio
mean
median
std
minimum
maximum
```

The output also stores:

```text
provider
collection
item_id
source_assets
target_gsd
qa_gsd
mask_policy
scale_applied
```

A scene-level `eo:cloud_cover` filter is useful for discovery but does not replace AOI-level quality metrics.

## 7. No global scene-rejection threshold yet

`eo2stats` does **not** currently reject a scene merely because `valid_pixel_ratio` is below a hard-coded threshold.

Reason:
- a suitable threshold depends on AOI size, research question, season and composite method;
- discarding observations at this stage can hide temporal data scarcity;
- the quality metrics themselves should remain available to the researcher.

A minimum valid-pixel threshold belongs to the later composite policy and must be recorded as provenance.

## 8. Python API

```python
from eo2stats import analyze_sentinel2_scene

results = analyze_sentinel2_scene(
    collection=scene.collection,
    item_id=scene.item_id,
    bbox_wgs84=(126.92, 37.35, 127.02, 37.43),
    indices=("ndvi", "ndwi", "mndwi", "ndbi"),
    mask_policy="research-clear-v1",
)

ndvi = results["ndvi"]
print(ndvi.summary.to_dict())
print(ndvi.provenance())
```

## 9. Time-series rule

For a time series, the same index definition and mask-policy version should be applied across all dates.

Do not mix:
- different mask policies without recording the transition;
- 10 m and 20 m versions of the same derived variable under the same variable name;
- raw DN-based indices and scaled-reflectance indices.

Recommended variable naming can retain the support where ambiguity is possible, for example:

```text
ndvi_s2_10m
ndbi_s2_20m
mndwi_s2_20m
```

The next processing stage will aggregate these scene-level rasters to monthly/seasonal composites and then to a stable Master Analysis Grid.
