from __future__ import annotations

from typing import Protocol, Sequence

from ..scenes import CollectionCoverage, SceneRecord, SceneSearchRequest


class SceneProvider(Protocol):
    name: str

    def resolve_collections(self, dataset: str) -> tuple[str, ...]: ...

    def search_scenes(self, request: SceneSearchRequest) -> list[SceneRecord]: ...

    def get_coverage(self, dataset: str) -> Sequence[CollectionCoverage]: ...
