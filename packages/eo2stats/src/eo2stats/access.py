from __future__ import annotations

from typing import Sequence

from .assets import AssetSpec, RasterWindowResult
from .providers.earth_search import EarthSearchProvider
from .raster import read_cog_bbox


def inspect_scene_assets(
    *,
    collection: str,
    item_id: str,
    provider: EarthSearchProvider | None = None,
) -> list[AssetSpec]:
    selected_provider = provider or EarthSearchProvider()
    return selected_provider.inspect_scene_assets(collection, item_id)


def read_scene_asset_bbox(
    *,
    collection: str,
    item_id: str,
    asset_key: str,
    bbox_wgs84: Sequence[float],
    apply_scale: bool = True,
    provider: EarthSearchProvider | None = None,
) -> RasterWindowResult:
    selected_provider = provider or EarthSearchProvider()
    specs = selected_provider.inspect_scene_assets(collection, item_id)
    try:
        asset = next(spec for spec in specs if spec.key == asset_key)
    except StopIteration as exc:
        available = ", ".join(spec.key for spec in specs)
        raise ValueError(
            f"Asset {asset_key!r} was not found on {item_id!r}. Available assets: {available}"
        ) from exc
    return read_cog_bbox(asset, bbox_wgs84, apply_scale=apply_scale)
