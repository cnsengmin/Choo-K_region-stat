from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping, Sequence

GeoJSON = Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class SceneSearchRequest:
    dataset: str
    start_date: str
    end_date: str
    bbox: tuple[float, float, float, float] | None = None
    intersects: GeoJSON | None = None
    max_cloud_cover: float | None = None
    limit: int | None = None

    def __post_init__(self) -> None:
        if (self.bbox is None) == (self.intersects is None):
            raise ValueError("Provide exactly one of bbox or intersects.")
        if self.max_cloud_cover is not None and not (0 <= self.max_cloud_cover <= 100):
            raise ValueError("max_cloud_cover must be between 0 and 100.")
        if self.limit is not None and self.limit < 1:
            raise ValueError("limit must be >= 1.")


@dataclass(frozen=True, slots=True)
class SceneRecord:
    provider: str
    collection: str
    item_id: str
    datetime: str | None
    platform: str | None
    cloud_cover: float | None
    bbox: tuple[float, float, float, float] | None
    geometry: dict[str, Any] | None
    asset_keys: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["bbox"] = list(self.bbox) if self.bbox is not None else None
        row["asset_keys"] = list(self.asset_keys)
        return row


@dataclass(frozen=True, slots=True)
class CollectionCoverage:
    provider: str
    collection: str
    spatial_bbox: tuple[float, float, float, float] | None
    temporal_intervals: tuple[tuple[str | None, str | None], ...]

    @classmethod
    def from_extent(
        cls,
        *,
        provider: str,
        collection: str,
        spatial_bbox: Sequence[float] | None,
        temporal_intervals: Sequence[Sequence[str | None]],
    ) -> "CollectionCoverage":
        bbox = tuple(float(v) for v in spatial_bbox) if spatial_bbox else None
        if bbox is not None and len(bbox) != 4:
            bbox = None
        intervals = tuple(
            (interval[0] if len(interval) > 0 else None, interval[1] if len(interval) > 1 else None)
            for interval in temporal_intervals
        )
        return cls(provider, collection, bbox, intervals)
