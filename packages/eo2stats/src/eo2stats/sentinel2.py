from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

from .assets import RasterWindowResult
from .providers.earth_search import EarthSearchProvider
from .raster import read_cog_bbox

SCL_CLASS_NAMES: dict[int, str] = {
    0: "no_data",
    1: "saturated_or_defective",
    2: "dark_area_pixels",
    3: "cloud_shadows",
    4: "vegetation",
    5: "bare_soils",
    6: "water",
    7: "low_cloud_probability_or_unclassified",
    8: "medium_cloud_probability",
    9: "high_cloud_probability",
    10: "thin_cirrus",
    11: "snow_or_ice",
}


@dataclass(frozen=True, slots=True)
class SCLMaskPolicy:
    name: str
    invalid_classes: frozenset[int]
    description: str


SCL_MASK_POLICIES: dict[str, SCLMaskPolicy] = {
    "research-clear-v1": SCLMaskPolicy(
        name="research-clear-v1",
        invalid_classes=frozenset({0, 1, 3, 7, 8, 9, 10, 11}),
        description=(
            "Urban/environmental research clear-sky mask. Keeps dark-area pixels but excludes "
            "nodata, defective pixels, cloud shadow, uncertain/cloud classes, cirrus and snow/ice."
        ),
    ),
    "research-strict-v1": SCLMaskPolicy(
        name="research-strict-v1",
        invalid_classes=frozenset({0, 1, 2, 3, 7, 8, 9, 10, 11}),
        description="Stricter research mask that also excludes dark-area pixels.",
    ),
    "copernicus-mosaic-like-v1": SCLMaskPolicy(
        name="copernicus-mosaic-like-v1",
        invalid_classes=frozenset({0, 1, 3, 7, 8, 9, 10}),
        description=(
            "Close to the Copernicus Sentinel-2 mosaic invalid-class rule, with class 0 "
            "explicitly treated as invalid. Snow/ice remains usable."
        ),
    ),
}


@dataclass(frozen=True, slots=True)
class Sentinel2IndexSpec:
    name: str
    a: str
    b: str
    reference: str
    target_gsd: int
    expression: str


INDEX_SPECS: dict[str, Sentinel2IndexSpec] = {
    "ndvi": Sentinel2IndexSpec("ndvi", "nir", "red", "red", 10, "(nir-red)/(nir+red)"),
    "ndwi": Sentinel2IndexSpec("ndwi", "green", "nir", "green", 10, "(green-nir)/(green+nir)"),
    "mndwi": Sentinel2IndexSpec(
        "mndwi", "green", "swir16", "swir16", 20, "(green-swir16)/(green+swir16)"
    ),
    "ndbi": Sentinel2IndexSpec(
        "ndbi", "swir16", "nir", "swir16", 20, "(swir16-nir)/(swir16+nir)"
    ),
}


@dataclass(frozen=True, slots=True)
class IndexSummary:
    n_total_pixels: int
    n_valid_pixels: int
    valid_pixel_ratio: float
    masked_pixel_ratio: float
    mean: float | None
    median: float | None
    std: float | None
    minimum: float | None
    maximum: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SpectralIndexResult:
    name: str
    data: Any
    crs: str
    transform: tuple[float, ...]
    target_gsd: float | None
    qa_gsd: float | None
    mask_policy: str
    source_assets: tuple[str, ...]
    provider: str
    collection: str
    item_id: str
    scale_applied: dict[str, bool]
    summary: IndexSummary

    def provenance(self) -> dict[str, Any]:
        return {
            "index": self.name,
            "provider": self.provider,
            "collection": self.collection,
            "item_id": self.item_id,
            "source_assets": list(self.source_assets),
            "target_gsd": self.target_gsd,
            "qa_gsd": self.qa_gsd,
            "mask_policy": self.mask_policy,
            "scale_applied": dict(self.scale_applied),
        }


def get_scl_mask_policy(name: str) -> SCLMaskPolicy:
    try:
        return SCL_MASK_POLICIES[name]
    except KeyError as exc:
        known = ", ".join(sorted(SCL_MASK_POLICIES))
        raise ValueError(f"Unknown SCL mask policy {name!r}. Known policies: {known}") from exc


def build_scl_valid_mask(scl: Any, *, policy: str = "research-clear-v1") -> Any:
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Sentinel-2 QA masking requires numpy. Install with `pip install 'eo2stats[eo]'`.") from exc

    selected = get_scl_mask_policy(policy)
    values = np.ma.asarray(scl)
    invalid = np.ma.getmaskarray(values).copy()
    filled = values.filled(0)
    invalid |= np.isin(filled, tuple(selected.invalid_classes))
    invalid |= ~np.isin(filled, tuple(SCL_CLASS_NAMES))
    return ~invalid


def _same_grid(left: RasterWindowResult, right: RasterWindowResult) -> bool:
    return (
        left.crs == right.crs
        and tuple(left.transform) == tuple(right.transform)
        and tuple(left.data.shape) == tuple(right.data.shape)
    )


def _align_to_reference(
    source: RasterWindowResult,
    reference: RasterWindowResult,
    *,
    categorical: bool,
) -> Any:
    try:
        import numpy as np
        from affine import Affine
        from rasterio.enums import Resampling
        from rasterio.warp import reproject
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Sentinel-2 band alignment requires numpy, rasterio and affine. "
            "Install with `pip install 'eo2stats[eo]'`."
        ) from exc

    if _same_grid(source, reference):
        return np.ma.asarray(source.data).copy()

    source_data = np.ma.asarray(source.data)
    src_transform = Affine(*source.transform)
    dst_transform = Affine(*reference.transform)
    target_shape = tuple(reference.data.shape)

    if categorical:
        src = source_data.filled(0).astype(np.int16)
        dst = np.zeros(target_shape, dtype=np.int16)
        resampling = Resampling.nearest
        src_nodata = 0
        dst_nodata = 0
    else:
        src = source_data.filled(np.nan).astype(np.float32)
        dst = np.full(target_shape, np.nan, dtype=np.float32)
        src_gsd = source.asset.gsd
        dst_gsd = reference.asset.gsd
        resampling = (
            Resampling.average
            if src_gsd is not None and dst_gsd is not None and src_gsd < dst_gsd
            else Resampling.bilinear
        )
        src_nodata = np.nan
        dst_nodata = np.nan

    reproject(
        source=src,
        destination=dst,
        src_transform=src_transform,
        src_crs=source.crs,
        dst_transform=dst_transform,
        dst_crs=reference.crs,
        src_nodata=src_nodata,
        dst_nodata=dst_nodata,
        resampling=resampling,
    )
    if categorical:
        return np.ma.array(dst, mask=(dst == 0))
    return np.ma.masked_invalid(dst)


def _summary(data: Any) -> IndexSummary:
    import numpy as np

    values = np.ma.masked_invalid(np.ma.asarray(data, dtype=np.float32))
    n_total = int(values.size)
    n_valid = int(values.count())
    ratio = (n_valid / n_total) if n_total else 0.0
    if n_valid:
        compressed = values.compressed()
        stats = (
            float(np.mean(compressed)),
            float(np.median(compressed)),
            float(np.std(compressed)),
            float(np.min(compressed)),
            float(np.max(compressed)),
        )
    else:
        stats = (None, None, None, None, None)
    return IndexSummary(
        n_total_pixels=n_total,
        n_valid_pixels=n_valid,
        valid_pixel_ratio=ratio,
        masked_pixel_ratio=(1.0 - ratio) if n_total else 0.0,
        mean=stats[0],
        median=stats[1],
        std=stats[2],
        minimum=stats[3],
        maximum=stats[4],
    )


def _validate_provenance(windows: Sequence[RasterWindowResult]) -> tuple[str, str, str]:
    provenance = {(w.asset.provider, w.asset.collection, w.asset.item_id) for w in windows}
    if len(provenance) != 1:
        raise ValueError("All Sentinel-2 inputs must come from the same provider/collection/item.")
    return next(iter(provenance))


def compute_sentinel2_index(
    name: str,
    *,
    bands: Mapping[str, RasterWindowResult],
    scl: RasterWindowResult,
    mask_policy: str = "research-clear-v1",
) -> SpectralIndexResult:
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Spectral-index calculation requires numpy. Install with `pip install 'eo2stats[eo]'`.") from exc

    key = name.lower()
    if key not in INDEX_SPECS:
        known = ", ".join(sorted(INDEX_SPECS))
        raise ValueError(f"Unknown Sentinel-2 index {name!r}. Known indices: {known}")
    spec = INDEX_SPECS[key]
    missing = [asset_key for asset_key in (spec.a, spec.b, spec.reference) if asset_key not in bands]
    if missing:
        raise ValueError(
            f"Missing required Sentinel-2 assets for {key}: {', '.join(sorted(set(missing)))}"
        )

    reference = bands[spec.reference]
    a = _align_to_reference(bands[spec.a], reference, categorical=False)
    b = _align_to_reference(bands[spec.b], reference, categorical=False)
    aligned_scl = _align_to_reference(scl, reference, categorical=True)
    valid_scl = build_scl_valid_mask(aligned_scl, policy=mask_policy)

    a_values = np.ma.filled(a, np.nan).astype(np.float32)
    b_values = np.ma.filled(b, np.nan).astype(np.float32)
    invalid = (
        np.ma.getmaskarray(a)
        | np.ma.getmaskarray(b)
        | ~valid_scl
        | ~np.isfinite(a_values)
        | ~np.isfinite(b_values)
    )
    numerator = a_values - b_values
    denominator = a_values + b_values
    invalid |= np.isclose(denominator, 0.0) | ~np.isfinite(denominator)
    with np.errstate(divide="ignore", invalid="ignore"):
        values = numerator / denominator
    result = np.ma.array(values, mask=invalid)

    provider_name, collection, item_id = _validate_provenance(
        [bands[spec.a], bands[spec.b], scl]
    )
    source_keys = tuple(dict.fromkeys((spec.a, spec.b, "scl")))
    scale_applied = {
        spec.a: bool(bands[spec.a].scale_applied),
        spec.b: bool(bands[spec.b].scale_applied),
        "scl": bool(scl.scale_applied),
    }
    return SpectralIndexResult(
        name=key,
        data=result,
        crs=reference.crs,
        transform=tuple(reference.transform),
        target_gsd=reference.asset.gsd,
        qa_gsd=scl.asset.gsd,
        mask_policy=mask_policy,
        source_assets=source_keys,
        provider=provider_name,
        collection=collection,
        item_id=item_id,
        scale_applied=scale_applied,
        summary=_summary(result),
    )


def analyze_sentinel2_scene(
    *,
    collection: str,
    item_id: str,
    bbox_wgs84: Sequence[float],
    indices: Sequence[str] = ("ndvi", "ndwi", "mndwi", "ndbi"),
    mask_policy: str = "research-clear-v1",
    provider: EarthSearchProvider | None = None,
) -> dict[str, SpectralIndexResult]:
    selected_provider = provider or EarthSearchProvider()
    requested = tuple(dict.fromkeys(name.lower() for name in indices))
    unknown = sorted(set(requested) - set(INDEX_SPECS))
    if unknown:
        known = ", ".join(sorted(INDEX_SPECS))
        raise ValueError(f"Unknown Sentinel-2 indices: {', '.join(unknown)}. Known indices: {known}")
    get_scl_mask_policy(mask_policy)

    assets = {spec.key: spec for spec in selected_provider.inspect_scene_assets(collection, item_id)}
    required = {"scl"}
    for name in requested:
        spec = INDEX_SPECS[name]
        required.update((spec.a, spec.b, spec.reference))
    missing = sorted(key for key in required if key not in assets)
    if missing:
        raise ValueError(
            f"Sentinel-2 item {item_id!r} is missing required assets: {', '.join(missing)}"
        )

    windows: dict[str, RasterWindowResult] = {}
    for key in sorted(required):
        windows[key] = read_cog_bbox(
            assets[key],
            bbox_wgs84,
            apply_scale=(key != "scl"),
        )

    bands = {key: value for key, value in windows.items() if key != "scl"}
    scl = windows["scl"]
    return {
        name: compute_sentinel2_index(
            name,
            bands=bands,
            scl=scl,
            mask_policy=mask_policy,
        )
        for name in requested
    }
