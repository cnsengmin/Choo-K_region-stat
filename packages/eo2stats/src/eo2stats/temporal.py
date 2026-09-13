from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from math import ceil, floor
from typing import Any, Iterable, Sequence

from .sentinel2 import SpectralIndexResult


@dataclass(frozen=True, slots=True)
class TemporalObservation:
    acquisition_datetime: str
    result: SpectralIndexResult

    @property
    def datetime(self) -> datetime:
        return _parse_datetime(self.acquisition_datetime)


@dataclass(frozen=True, slots=True)
class CompositePolicy:
    name: str = "temporal-composite-v1"
    method: str = "median"
    percentile: float | None = None
    min_scene_valid_ratio: float = 0.0
    min_observations: int = 1
    resampling: str = "bilinear"

    def __post_init__(self) -> None:
        method = self.method.lower()
        if method not in {"median", "mean", "percentile"}:
            raise ValueError("method must be 'median', 'mean', or 'percentile'.")
        if method == "percentile":
            if self.percentile is None or not 0 <= self.percentile <= 100:
                raise ValueError("percentile method requires percentile between 0 and 100.")
        elif self.percentile is not None:
            raise ValueError("percentile may only be set when method='percentile'.")
        if not 0 <= self.min_scene_valid_ratio <= 1:
            raise ValueError("min_scene_valid_ratio must be between 0 and 1.")
        if self.min_observations < 1:
            raise ValueError("min_observations must be at least 1.")
        if self.resampling not in {"nearest", "bilinear"}:
            raise ValueError("resampling must be 'nearest' or 'bilinear'.")


@dataclass(frozen=True, slots=True)
class CompositeGrid:
    crs: str
    transform: tuple[float, ...]
    shape: tuple[int, int]
    target_gsd: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "crs": self.crs,
            "transform": list(self.transform),
            "shape": list(self.shape),
            "target_gsd": self.target_gsd,
        }


@dataclass(frozen=True, slots=True)
class CompositeSummary:
    input_scene_count: int
    usable_scene_count: int
    rejected_scene_count: int
    n_total_pixels: int
    n_valid_pixels: int
    valid_area_ratio: float
    mean_observations: float
    max_observations: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class TemporalCompositeResult:
    index_name: str
    period_key: str
    data: Any
    n_observations: Any
    crs: str
    transform: tuple[float, ...]
    target_gsd: float
    mask_policy: str
    composite_policy: CompositePolicy
    source_item_ids: tuple[str, ...]
    source_datetimes: tuple[str, ...]
    source_collections: tuple[str, ...]
    rejected_item_ids: tuple[str, ...]
    summary: CompositeSummary

    def provenance(self) -> dict[str, Any]:
        return {
            "index": self.index_name,
            "period_key": self.period_key,
            "crs": self.crs,
            "transform": list(self.transform),
            "target_gsd": self.target_gsd,
            "mask_policy": self.mask_policy,
            "composite_policy": asdict(self.composite_policy),
            "source_item_ids": list(self.source_item_ids),
            "source_datetimes": list(self.source_datetimes),
            "source_collections": list(self.source_collections),
            "rejected_item_ids": list(self.rejected_item_ids),
            "summary": self.summary.to_dict(),
        }


def _parse_datetime(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    text = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"Invalid acquisition datetime {value!r}; use ISO-8601.") from exc


def temporal_group_key(value: str | datetime, frequency: str = "monthly") -> str:
    dt = _parse_datetime(value)
    freq = frequency.lower()
    if freq == "monthly":
        return f"{dt.year:04d}-{dt.month:02d}"
    if freq == "annual":
        return f"{dt.year:04d}"
    if freq == "seasonal":
        if dt.month in (12, 1, 2):
            season = "DJF"
            season_year = dt.year + 1 if dt.month == 12 else dt.year
        elif dt.month in (3, 4, 5):
            season = "MAM"
            season_year = dt.year
        elif dt.month in (6, 7, 8):
            season = "JJA"
            season_year = dt.year
        else:
            season = "SON"
            season_year = dt.year
        return f"{season_year:04d}-{season}"
    raise ValueError("frequency must be 'monthly', 'seasonal', or 'annual'.")


def group_temporal_observations(
    observations: Iterable[TemporalObservation],
    *,
    frequency: str = "monthly",
) -> dict[str, list[TemporalObservation]]:
    grouped: dict[str, list[TemporalObservation]] = {}
    for observation in observations:
        key = temporal_group_key(observation.datetime, frequency)
        grouped.setdefault(key, []).append(observation)
    for values in grouped.values():
        values.sort(key=lambda obs: (obs.datetime, obs.result.item_id))
    return dict(sorted(grouped.items()))


def _validate_observations(
    observations: Sequence[TemporalObservation],
) -> tuple[str, float, str]:
    if not observations:
        raise ValueError("At least one temporal observation is required.")
    index_names = {obs.result.name for obs in observations}
    if len(index_names) != 1:
        raise ValueError("A temporal composite may contain only one spectral index.")
    mask_policies = {obs.result.mask_policy for obs in observations}
    if len(mask_policies) != 1:
        raise ValueError("All observations in a composite must use the same QA mask policy.")
    target_gsds = {
        float(obs.result.target_gsd)
        for obs in observations
        if obs.result.target_gsd is not None
    }
    if len(target_gsds) != 1:
        raise ValueError("All observations must have one consistent non-null target GSD.")
    return next(iter(index_names)), next(iter(target_gsds)), next(iter(mask_policies))


def build_composite_grid(
    observations: Sequence[TemporalObservation],
    *,
    target_gsd: float | None = None,
) -> CompositeGrid:
    try:
        from affine import Affine
        from rasterio.transform import array_bounds, from_origin
        from rasterio.warp import transform_bounds
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Temporal composites require rasterio and affine. "
            "Install with `pip install 'eo2stats[eo]'`."
        ) from exc

    if not observations:
        raise ValueError(
            "At least one temporal observation is required to build a composite grid."
        )
    _, inferred_gsd, _ = _validate_observations(observations)
    grid_gsd = inferred_gsd if target_gsd is None else float(target_gsd)
    if grid_gsd <= 0:
        raise ValueError("target_gsd must be positive.")

    target_crs = observations[0].result.crs
    bounds: list[tuple[float, float, float, float]] = []
    for observation in observations:
        result = observation.result
        height, width = result.data.shape
        src_transform = Affine(*result.transform)
        west, south, east, north = array_bounds(height, width, src_transform)
        if result.crs != target_crs:
            west, south, east, north = transform_bounds(
                result.crs,
                target_crs,
                west,
                south,
                east,
                north,
                densify_pts=21,
            )
        bounds.append((west, south, east, north))

    left = floor(min(bound[0] for bound in bounds) / grid_gsd) * grid_gsd
    bottom = floor(min(bound[1] for bound in bounds) / grid_gsd) * grid_gsd
    right = ceil(max(bound[2] for bound in bounds) / grid_gsd) * grid_gsd
    top = ceil(max(bound[3] for bound in bounds) / grid_gsd) * grid_gsd
    width = max(1, int(round((right - left) / grid_gsd)))
    height = max(1, int(round((top - bottom) / grid_gsd)))
    transform = from_origin(left, top, grid_gsd, grid_gsd)
    return CompositeGrid(
        crs=target_crs,
        transform=tuple(transform)[:6],
        shape=(height, width),
        target_gsd=grid_gsd,
    )


def _align_index_result(
    result: SpectralIndexResult,
    *,
    target_crs: str,
    target_transform: tuple[float, ...],
    target_shape: tuple[int, int],
    resampling: str,
) -> Any:
    try:
        import numpy as np
        from affine import Affine
        from rasterio.enums import Resampling
        from rasterio.warp import reproject
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Temporal composites require numpy, rasterio and affine. "
            "Install with `pip install 'eo2stats[eo]'`."
        ) from exc

    source = np.ma.masked_invalid(np.ma.asarray(result.data, dtype=np.float32))
    source_transform = Affine(*result.transform)
    destination_transform = Affine(*target_transform)
    if (
        result.crs == target_crs
        and tuple(result.transform) == tuple(target_transform)
        and tuple(source.shape) == tuple(target_shape)
    ):
        return source.copy()

    destination = np.full(target_shape, np.nan, dtype=np.float32)
    mode = Resampling.nearest if resampling == "nearest" else Resampling.bilinear
    reproject(
        source=source.filled(np.nan),
        destination=destination,
        src_transform=source_transform,
        src_crs=result.crs,
        dst_transform=destination_transform,
        dst_crs=target_crs,
        src_nodata=np.nan,
        dst_nodata=np.nan,
        resampling=mode,
    )
    return np.ma.masked_invalid(destination)


def composite_observations(
    observations: Sequence[TemporalObservation],
    *,
    period_key: str,
    policy: CompositePolicy | None = None,
    grid: CompositeGrid | None = None,
) -> TemporalCompositeResult:
    try:
        import numpy as np
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Temporal composites require numpy. Install with `pip install 'eo2stats[eo]'`."
        ) from exc

    selected_policy = policy or CompositePolicy()
    index_name, target_gsd, mask_policy = _validate_observations(observations)
    selected_grid = grid or build_composite_grid(
        observations, target_gsd=target_gsd
    )
    if not abs(selected_grid.target_gsd - target_gsd) < 1e-9:
        raise ValueError(
            f"Composite grid GSD {selected_grid.target_gsd} does not match "
            f"the index target GSD {target_gsd}."
        )
    target_crs = selected_grid.crs
    target_transform = selected_grid.transform
    target_shape = selected_grid.shape

    usable = [
        obs
        for obs in observations
        if obs.result.summary.valid_pixel_ratio >= selected_policy.min_scene_valid_ratio
    ]
    rejected = [
        obs
        for obs in observations
        if obs.result.summary.valid_pixel_ratio < selected_policy.min_scene_valid_ratio
    ]

    if usable:
        aligned = [
            _align_index_result(
                obs.result,
                target_crs=target_crs,
                target_transform=target_transform,
                target_shape=target_shape,
                resampling=selected_policy.resampling,
            )
            for obs in usable
        ]
        stack = np.ma.stack(aligned)
        filled = stack.filled(np.nan).astype(np.float32)
        n_observations = np.sum(np.isfinite(filled), axis=0).astype(np.uint16)
        import warnings

        method = selected_policy.method.lower()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            if method == "mean":
                composite = np.nanmean(filled, axis=0)
            elif method == "median":
                composite = np.nanmedian(filled, axis=0)
            else:
                composite = np.nanpercentile(
                    filled,
                    selected_policy.percentile,
                    axis=0,
                )
    else:
        n_observations = np.zeros(target_shape, dtype=np.uint16)
        composite = np.full(target_shape, np.nan, dtype=np.float32)

    mask = (~np.isfinite(composite)) | (
        n_observations < selected_policy.min_observations
    )
    data = np.ma.array(composite.astype(np.float32), mask=mask)
    n_total = int(data.size)
    n_valid = int(data.count())
    valid_area_ratio = (n_valid / n_total) if n_total else 0.0
    mean_observations = float(np.mean(n_observations)) if n_total else 0.0
    max_observations = int(np.max(n_observations)) if n_total else 0

    return TemporalCompositeResult(
        index_name=index_name,
        period_key=period_key,
        data=data,
        n_observations=n_observations,
        crs=target_crs,
        transform=target_transform,
        target_gsd=target_gsd,
        mask_policy=mask_policy,
        composite_policy=selected_policy,
        source_item_ids=tuple(obs.result.item_id for obs in usable),
        source_datetimes=tuple(obs.acquisition_datetime for obs in usable),
        source_collections=tuple(
            dict.fromkeys(obs.result.collection for obs in usable)
        ),
        rejected_item_ids=tuple(obs.result.item_id for obs in rejected),
        summary=CompositeSummary(
            input_scene_count=len(observations),
            usable_scene_count=len(usable),
            rejected_scene_count=len(rejected),
            n_total_pixels=n_total,
            n_valid_pixels=n_valid,
            valid_area_ratio=valid_area_ratio,
            mean_observations=mean_observations,
            max_observations=max_observations,
        ),
    )


def build_temporal_composites(
    observations: Sequence[TemporalObservation],
    *,
    frequency: str = "monthly",
    policy: CompositePolicy | None = None,
    grid: CompositeGrid | None = None,
) -> dict[str, TemporalCompositeResult]:
    _, target_gsd, _ = _validate_observations(observations)
    selected_grid = grid or build_composite_grid(
        observations, target_gsd=target_gsd
    )
    grouped = group_temporal_observations(observations, frequency=frequency)
    return {
        period_key: composite_observations(
            values,
            period_key=period_key,
            policy=policy,
            grid=selected_grid,
        )
        for period_key, values in grouped.items()
    }
