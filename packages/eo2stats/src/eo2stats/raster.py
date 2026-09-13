from __future__ import annotations

from typing import Sequence

from .assets import AssetSpec, RasterWindowResult


def read_cog_bbox(
    asset: AssetSpec,
    bbox_wgs84: Sequence[float],
    *,
    apply_scale: bool = True,
) -> RasterWindowResult:
    if not asset.is_cog:
        raise ValueError(f"Asset {asset.key!r} is not declared as a COG.")
    if len(bbox_wgs84) != 4:
        raise ValueError("bbox_wgs84 must contain minx, miny, maxx, maxy.")

    try:
        import numpy as np
        import rasterio
        from rasterio.errors import WindowError
        from rasterio.warp import transform_bounds
        from rasterio.windows import Window, from_bounds, intersection
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "COG reading requires rasterio and numpy. Install with `pip install 'eo2stats[eo]'`."
        ) from exc

    bbox = tuple(float(v) for v in bbox_wgs84)
    with rasterio.open(asset.href) as src:
        if src.crs is None:
            raise ValueError(f"Raster asset {asset.key!r} has no CRS metadata.")
        target_bounds = transform_bounds("EPSG:4326", src.crs, *bbox, densify_pts=21)
        requested = from_bounds(*target_bounds, transform=src.transform).round_offsets().round_lengths()
        full = Window(0, 0, src.width, src.height)
        try:
            window = intersection(requested, full)
        except WindowError as exc:
            raise ValueError("Requested bbox does not intersect the raster asset.") from exc
        data = src.read(1, window=window, masked=True)
        out_transform = src.window_transform(window)
        crs = src.crs.to_string()

    can_scale = asset.kind not in {"classification", "probability", "visual", "metadata"}
    scale_applied = bool(apply_scale and can_scale and (asset.scale is not None or asset.offset is not None))
    if scale_applied:
        scale = 1.0 if asset.scale is None else asset.scale
        offset = 0.0 if asset.offset is None else asset.offset
        data = data.astype(np.float32) * scale + offset

    return RasterWindowResult(
        asset=asset,
        data=data,
        crs=crs,
        transform=tuple(out_transform)[:6],
        bbox_wgs84=bbox,
        scale_applied=scale_applied,
    )
