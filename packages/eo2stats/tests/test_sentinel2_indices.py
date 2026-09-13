from __future__ import annotations

import numpy as np
import pytest
from affine import Affine

from eo2stats.assets import AssetSpec, RasterWindowResult
from eo2stats.sentinel2 import (
    analyze_sentinel2_scene,
    build_scl_valid_mask,
    compute_sentinel2_index,
)


def _window(
    key: str,
    gsd: float,
    data: np.ndarray,
    transform: Affine,
    *,
    item_id: str = "scene-1",
    kind: str = "reflectance",
    scale_applied: bool = True,
) -> RasterWindowResult:
    asset = AssetSpec(
        provider="earth-search",
        collection="sentinel-2-c1-l2a",
        item_id=item_id,
        key=key,
        href=f"memory://{key}.tif",
        media_type="image/tiff; application=geotiff; profile=cloud-optimized",
        roles=("data",),
        title=key,
        gsd=gsd,
        data_type="uint8" if kind == "classification" else "uint16",
        nodata=0,
        unit=None,
        scale=None if kind == "classification" else 0.0001,
        offset=None if kind == "classification" else -0.1,
        kind=kind,
        is_cog=True,
    )
    return RasterWindowResult(
        asset=asset,
        data=np.ma.array(data),
        crs="EPSG:32652",
        transform=tuple(transform)[:6],
        bbox_wgs84=(126.9, 37.3, 127.0, 37.4),
        scale_applied=scale_applied,
    )


def test_research_clear_mask_keeps_dark_area_but_excludes_cloud_and_snow() -> None:
    scl = np.arange(12, dtype=np.int16).reshape(3, 4)
    valid = build_scl_valid_mask(scl, policy="research-clear-v1")
    assert set(np.flatnonzero(valid)) == {2, 4, 5, 6}


def test_research_strict_mask_also_excludes_dark_area() -> None:
    scl = np.arange(12, dtype=np.int16).reshape(3, 4)
    valid = build_scl_valid_mask(scl, policy="research-strict-v1")
    assert set(np.flatnonzero(valid)) == {4, 5, 6}


def test_ndvi_uses_10m_grid_and_nearest_scl_mask() -> None:
    transform10 = Affine(10, 0, 0, 0, -10, 40)
    transform20 = Affine(20, 0, 0, 0, -20, 40)
    red = _window("red", 10, np.full((4, 4), 0.2), transform10)
    nir = _window("nir", 10, np.full((4, 4), 0.6), transform10)
    scl = _window(
        "scl",
        20,
        np.array([[4, 9], [4, 4]], dtype=np.uint8),
        transform20,
        kind="classification",
        scale_applied=False,
    )

    result = compute_sentinel2_index(
        "ndvi",
        bands={"red": red, "nir": nir},
        scl=scl,
    )

    assert result.data.shape == (4, 4)
    assert result.target_gsd == 10
    assert result.qa_gsd == 20
    assert result.summary.n_valid_pixels == 12
    assert result.summary.valid_pixel_ratio == pytest.approx(0.75)
    assert result.summary.masked_pixel_ratio == pytest.approx(0.25)
    assert np.allclose(result.data.compressed(), 0.5, atol=1e-6)


def test_ndbi_downsamples_nir_to_native_20m_swir_grid() -> None:
    transform10 = Affine(10, 0, 0, 0, -10, 40)
    transform20 = Affine(20, 0, 0, 0, -20, 40)
    nir = _window("nir", 10, np.full((4, 4), 0.6), transform10)
    swir = _window("swir16", 20, np.full((2, 2), 0.4), transform20)
    scl = _window(
        "scl",
        20,
        np.full((2, 2), 5, dtype=np.uint8),
        transform20,
        kind="classification",
        scale_applied=False,
    )

    result = compute_sentinel2_index(
        "ndbi",
        bands={"nir": nir, "swir16": swir},
        scl=scl,
    )

    assert result.data.shape == (2, 2)
    assert result.target_gsd == 20
    assert np.allclose(result.data.compressed(), -0.2, atol=1e-6)


def test_inputs_from_different_items_are_rejected() -> None:
    transform = Affine(10, 0, 0, 0, -10, 20)
    red = _window("red", 10, np.full((2, 2), 0.2), transform, item_id="scene-a")
    nir = _window("nir", 10, np.full((2, 2), 0.6), transform, item_id="scene-b")
    scl = _window(
        "scl",
        10,
        np.full((2, 2), 4, dtype=np.uint8),
        transform,
        item_id="scene-a",
        kind="classification",
        scale_applied=False,
    )

    with pytest.raises(ValueError, match="same provider/collection/item"):
        compute_sentinel2_index("ndvi", bands={"red": red, "nir": nir}, scl=scl)


def test_high_level_scene_analysis_reads_only_required_assets(monkeypatch: pytest.MonkeyPatch) -> None:
    transform10 = Affine(10, 0, 0, 0, -10, 20)
    specs = {
        key: _window(
            key,
            10,
            np.full((2, 2), 4 if key == "scl" else 1),
            transform10,
            kind="classification" if key == "scl" else "reflectance",
            scale_applied=(key != "scl"),
        ).asset
        for key in ("red", "nir", "green", "scl")
    }

    class FakeProvider:
        def inspect_scene_assets(self, collection: str, item_id: str) -> list[AssetSpec]:
            assert collection == "sentinel-2-c1-l2a"
            assert item_id == "scene-1"
            return list(specs.values())

    read_keys: list[str] = []

    def fake_read(asset: AssetSpec, bbox_wgs84, *, apply_scale: bool = True) -> RasterWindowResult:
        read_keys.append(asset.key)
        value = 4 if asset.key == "scl" else {"red": 0.2, "nir": 0.6, "green": 0.3}[asset.key]
        return _window(
            asset.key,
            10,
            np.full((2, 2), value),
            transform10,
            kind="classification" if asset.key == "scl" else "reflectance",
            scale_applied=(asset.key != "scl"),
        )

    monkeypatch.setattr("eo2stats.sentinel2.read_cog_bbox", fake_read)
    result = analyze_sentinel2_scene(
        collection="sentinel-2-c1-l2a",
        item_id="scene-1",
        bbox_wgs84=(126.9, 37.3, 127.0, 37.4),
        indices=("ndvi", "ndwi"),
        provider=FakeProvider(),
    )

    assert set(result) == {"ndvi", "ndwi"}
    assert set(read_keys) == {"red", "nir", "green", "scl"}
    assert result["ndvi"].summary.valid_pixel_ratio == 1.0
