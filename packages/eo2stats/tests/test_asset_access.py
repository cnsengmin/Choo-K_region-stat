from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from eo2stats.assets import AssetSpec, asset_specs_from_item
from eo2stats.raster import read_cog_bbox


def test_asset_inspection_merges_collection_item_assets_metadata():
    collection = SimpleNamespace(
        id="sentinel-2-c1-l2a",
        extra_fields={
            "item_assets": {
                "red": {
                    "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                    "title": "Red - 10m",
                    "gsd": 10,
                    "roles": ["data", "reflectance"],
                    "raster:bands": [
                        {"data_type": "uint16", "nodata": 0, "scale": 0.0001, "offset": -0.1}
                    ],
                },
                "scl": {
                    "type": "image/tiff; application=geotiff; profile=cloud-optimized",
                    "title": "Scene classification",
                    "gsd": 20,
                    "roles": ["data"],
                    "raster:bands": [{"data_type": "uint8", "nodata": 0}],
                },
            }
        },
    )
    asset_cls = lambda href, roles=None: SimpleNamespace(
        href=href,
        roles=roles,
        media_type=None,
        title=None,
        extra_fields={},
    )
    item = SimpleNamespace(
        id="S2_TEST",
        collection_id="sentinel-2-c1-l2a",
        assets={
            "red": asset_cls("https://example/red.tif", ["data", "reflectance"]),
            "scl": asset_cls("https://example/scl.tif", ["data"]),
        },
    )

    specs = {
        spec.key: spec
        for spec in asset_specs_from_item(
            provider_name="earth-search", collection=collection, item=item
        )
    }

    assert specs["red"].scale == 0.0001
    assert specs["red"].offset == -0.1
    assert specs["red"].kind == "reflectance"
    assert specs["red"].is_cog is True
    assert specs["scl"].kind == "classification"


def test_read_cog_bbox_reads_only_intersection_and_applies_scale(tmp_path: Path):
    path = tmp_path / "test.tif"
    data = np.arange(100, dtype=np.uint16).reshape(10, 10)
    transform = from_origin(126.9, 37.5, 0.01, 0.01)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=10,
        height=10,
        count=1,
        dtype="uint16",
        crs="EPSG:4326",
        transform=transform,
        nodata=0,
        tiled=True,
    ) as dst:
        dst.write(data, 1)

    asset = AssetSpec(
        provider="test",
        collection="test",
        item_id="item",
        key="red",
        href=str(path),
        media_type="image/tiff; application=geotiff; profile=cloud-optimized",
        roles=("data", "reflectance"),
        title="Red",
        gsd=10,
        data_type="uint16",
        nodata=0,
        unit=None,
        scale=0.01,
        offset=-1.0,
        kind="reflectance",
        is_cog=True,
    )

    result = read_cog_bbox(asset, (126.92, 37.42, 126.96, 37.46))

    assert result.data.shape[0] < 10
    assert result.data.shape[1] < 10
    assert result.scale_applied is True
    assert result.crs == "EPSG:4326"


def test_classification_asset_is_not_scaled(tmp_path: Path):
    path = tmp_path / "scl.tif"
    data = np.full((4, 4), 4, dtype=np.uint8)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=4,
        height=4,
        count=1,
        dtype="uint8",
        crs="EPSG:4326",
        transform=from_origin(126.9, 37.5, 0.01, 0.01),
    ) as dst:
        dst.write(data, 1)

    asset = AssetSpec(
        provider="test",
        collection="test",
        item_id="item",
        key="scl",
        href=str(path),
        media_type="image/tiff; application=geotiff; profile=cloud-optimized",
        roles=("data",),
        title="SCL",
        gsd=20,
        data_type="uint8",
        nodata=0,
        unit=None,
        scale=0.0001,
        offset=-0.1,
        kind="classification",
        is_cog=True,
    )

    result = read_cog_bbox(asset, (126.90, 37.46, 126.94, 37.50))
    assert result.scale_applied is False
    assert np.all(result.data.compressed() == 4)


def test_non_cog_is_rejected():
    asset = AssetSpec(
        provider="test",
        collection="test",
        item_id="item",
        key="x",
        href="x.jp2",
        media_type="image/jp2",
        roles=("data",),
        title=None,
        gsd=None,
        data_type=None,
        nodata=None,
        unit=None,
        scale=None,
        offset=None,
        kind="measurement",
        is_cog=False,
    )
    with pytest.raises(ValueError):
        read_cog_bbox(asset, (0, 0, 1, 1))
