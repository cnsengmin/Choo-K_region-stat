# STAC scene search

This module is the first executable Earth-observation workflow in `eo2stats`.

Its job is intentionally narrow:

```text
AOI + time range + logical dataset
              ↓
        STAC discovery
              ↓
item_id / datetime / platform / cloud / footprint / asset keys
```

It does **not** download full imagery or compute indices yet.

## Why a logical dataset name?

Provider collection IDs are not stable enough to leak into every research script.

For example, Earth Search currently separates Sentinel-2 L2A into:

```text
sentinel-2-pre-c1-l2a
sentinel-2-c1-l2a
```

`eo2stats` exposes the logical dataset:

```text
sentinel-2-l2a
```

and resolves it to the required provider collections internally.

This matters for long time series because a single scientific dataset may span multiple provider-side collections after archive reprocessing or product-version changes.

## Installation

```bash
pip install -e '.[eo]'
```

The `eo` extra installs `pystac-client` and raster libraries that will be used in later phases.

## Basic search

```python
from eo2stats import search_scenes

scenes = search_scenes(
    dataset="sentinel-2-l2a",
    start_date="2026-08-01",
    end_date="2026-08-31",
    bbox=(126.92, 37.35, 127.02, 37.43),
    max_cloud_cover=20,
    limit=100,
)

rows = [scene.to_dict() for scene in scenes]
```

The bbox above is only a smoke-test window around the Anyang/Pyeongchon area. It is **not** an authoritative administrative boundary.

For research, pass the actual study-area geometry whenever possible.

## GeoJSON AOI

A GeoJSON Geometry or Feature can be used.

```python
scenes = search_scenes(
    dataset="sentinel-2-l2a",
    start_date="2024-01-01",
    end_date="2024-12-31",
    intersects=study_area_feature,
    max_cloud_cover=30,
)
```

## Result schema

Each `SceneRecord` contains:

```text
provider
collection
item_id
datetime
platform
cloud_cover
bbox
geometry
asset_keys
```

These fields are discovery metadata, not yet analysis values.

## Dataset coverage

Do not hard-code mission start/end dates into analysis code.

Use current STAC collection metadata:

```python
from eo2stats import get_dataset_coverage

coverage = get_dataset_coverage("sentinel-2-l2a")
```

This returns provider collection spatial and temporal extents. The result is useful for validating whether a requested period is even represented by the current provider catalog.

## Cloud-cover warning

`eo:cloud_cover` describes scene/tile-level metadata. It does **not** guarantee that the study AOI is cloud-free.

The later raster phase must calculate:

```text
AOI valid pixel ratio
AOI cloud/shadow fraction
usable pixel count
```

from SCL/cloud assets.

## Current provider

Initial provider:

- Element 84 Earth Search v1
- endpoint: `https://earth-search.aws.element84.com/v1`

The provider interface is separated from the public search API so that Copernicus Data Space or another STAC provider can be added without changing analysis scripts.

## Next phase

After scene discovery is stable:

1. choose an Item
2. inspect asset metadata and scale/offset
3. read only AOI windows from COG assets
4. apply QA/cloud mask
5. compute NDVI/NDBI/NDWI
6. aggregate to the Master Analysis Grid
7. preserve the Item IDs used for every derived observation
