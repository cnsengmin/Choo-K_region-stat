from __future__ import annotations

from typing import Any

from .providers.earth_search import EarthSearchProvider
from .scenes import CollectionCoverage, SceneRecord, SceneSearchRequest


def search_scenes(
    *,
    dataset: str,
    start_date: str,
    end_date: str,
    bbox: tuple[float, float, float, float] | None = None,
    intersects: dict[str, Any] | None = None,
    max_cloud_cover: float | None = None,
    limit: int | None = None,
    provider: EarthSearchProvider | None = None,
) -> list[SceneRecord]:
    selected_provider = provider or EarthSearchProvider()
    request = SceneSearchRequest(
        dataset=dataset,
        start_date=start_date,
        end_date=end_date,
        bbox=bbox,
        intersects=intersects,
        max_cloud_cover=max_cloud_cover,
        limit=limit,
    )
    return selected_provider.search_scenes(request)


def get_dataset_coverage(
    dataset: str,
    *,
    provider: EarthSearchProvider | None = None,
) -> list[CollectionCoverage]:
    selected_provider = provider or EarthSearchProvider()
    return list(selected_provider.get_coverage(dataset))
