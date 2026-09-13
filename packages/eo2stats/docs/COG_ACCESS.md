# COG asset inspection and AOI window reading

This stage connects STAC discovery to actual raster values without downloading complete scenes.

## Workflow

```text
search_scenes(...)
      ↓
SceneRecord(collection, item_id, asset_keys)
      ↓
inspect_scene_assets(...)
      ↓
AssetSpec(href, gsd, dtype, nodata, scale, offset, roles)
      ↓
read_scene_asset_bbox(...)
      ↓
AOI raster window + provenance
```

## Inspect an Item

```python
from eo2stats import inspect_scene_assets

assets = inspect_scene_assets(
    collection="sentinel-2-c1-l2a",
    item_id="<STAC ITEM ID>",
)

for asset in assets:
    print(asset.to_dict())
```

Expected analytical Sentinel-2 keys include assets such as:

```text
red
nir
swir16
swir22
scl
cloud
```

The exact Item must be inspected rather than assuming every provider exposes identical keys.

## Metadata precedence

STAC can describe raster metadata at both Item Asset and Collection `item_assets` levels.

`eo2stats` uses:

```text
Collection item_assets metadata
          ↓ fallback
Item asset metadata
          ↓ override
AssetSpec
```

Fields currently extracted:

- href
- media type
- roles
- title
- GSD
- raster data type
- nodata
- unit
- scale
- offset
- semantic kind
- whether the media type declares a Cloud Optimized GeoTIFF

## Read only the AOI window

```python
from eo2stats import read_scene_asset_bbox

window = read_scene_asset_bbox(
    collection="sentinel-2-c1-l2a",
    item_id="<STAC ITEM ID>",
    asset_key="red",
    bbox_wgs84=(126.92, 37.35, 127.02, 37.43),
)

array = window.data
```

The bbox is supplied in EPSG:4326. `eo2stats` transforms the bounds to the asset CRS, calculates the intersecting raster window, and asks rasterio to read only that window.

For a remote COG, GDAL/rasterio can use HTTP range requests rather than transferring the complete raster when the remote server supports them.

## Scale and offset

Never infer a physical-value conversion only from the mission name.

Current rule:

```text
STAC raster:bands scale/offset available?
        ↓ yes
measurement / reflectance asset?
        ↓ yes
physical = stored_value × scale + offset
```

Classification, probability, visual and metadata assets are not automatically scaled.

Examples:

- Sentinel-2 reflectance: scale/offset may be applied from STAC metadata.
- Sentinel-2 SCL: categorical codes; do not convert to reflectance.
- Cloud probability: preserve its declared probability encoding.
- Landsat SR/ST later: use each asset's declared scaling rather than a Sentinel formula.

## Raw values

To preserve stored values:

```python
window = read_scene_asset_bbox(
    collection="...",
    item_id="...",
    asset_key="red",
    bbox_wgs84=(...),
    apply_scale=False,
)
```

Both the asset metadata and `scale_applied` flag remain available in the result.

## Current limitation

The first reader accepts a WGS84 bbox. Polygon masking will be added after the bbox path is stable.

This is intentional: STAC discovery already accepts exact GeoJSON geometry, while the first raster I/O milestone focuses on reliable cloud-native window reads and scale semantics.

## Next

The next processing layer should combine multiple aligned assets for one Item:

```text
red + nir + SCL
      ↓
cloud / shadow mask
      ↓
NDVI
      ↓
AOI valid-pixel statistics
```

Then multiple Items can be composed into monthly/seasonal observations and aggregated to the Master Analysis Grid.
