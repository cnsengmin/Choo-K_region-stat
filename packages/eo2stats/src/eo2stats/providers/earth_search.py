from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from ..assets import AssetSpec, asset_specs_from_item
from ..scenes import CollectionCoverage, SceneRecord, SceneSearchRequest

EARTH_SEARCH_URL = "https://earth-search.aws.element84.com/v1"

# Logical dataset aliases are intentionally separated from provider collection IDs.
# Earth Search split Sentinel-2 L2A around Copernicus Collection-1 processing.
DATASET_COLLECTIONS: dict[str, tuple[str, ...]] = {
    "sentinel-2-l2a": ("sentinel-2-pre-c1-l2a", "sentinel-2-c1-l2a"),
    "landsat-c2-l2": ("landsat-c2-l2",),
    "sentinel-1-grd": ("sentinel-1",),
    "cop-dem-glo-30": ("cop-dem-glo-30",),
}


def _normalize_intersects(value: Mapping[str, Any]) -> Mapping[str, Any]:
    if value.get("type") == "Feature":
        geometry = value.get("geometry")
        if not isinstance(geometry, Mapping):
            raise ValueError("GeoJSON Feature must contain a geometry object.")
        return geometry
    return value


def _datetime_to_iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


class EarthSearchProvider:
    name = "earth-search"

    def __init__(self, client: Any | None = None, *, url: str = EARTH_SEARCH_URL) -> None:
        self.url = url
        self._client = client

    @property
    def client(self) -> Any:
        if self._client is None:
            try:
                from pystac_client import Client
            except ImportError as exc:  # pragma: no cover - depends on optional extra
                raise RuntimeError(
                    "Earth Search support requires pystac-client. "
                    "Install with `pip install 'eo2stats[eo]'`."
                ) from exc
            self._client = Client.open(self.url)
        return self._client

    def resolve_collections(self, dataset: str) -> tuple[str, ...]:
        try:
            return DATASET_COLLECTIONS[dataset]
        except KeyError as exc:
            known = ", ".join(sorted(DATASET_COLLECTIONS))
            raise ValueError(f"Unknown Earth Search dataset {dataset!r}. Known datasets: {known}") from exc

    def search_scenes(self, request: SceneSearchRequest) -> list[SceneRecord]:
        collections = self.resolve_collections(request.dataset)
        params: dict[str, Any] = {
            "collections": list(collections),
            "datetime": f"{request.start_date}/{request.end_date}",
        }
        if request.limit is not None:
            params["max_items"] = request.limit
        if request.bbox is not None:
            params["bbox"] = list(request.bbox)
        else:
            assert request.intersects is not None
            params["intersects"] = _normalize_intersects(request.intersects)
        if request.max_cloud_cover is not None:
            params["query"] = {"eo:cloud_cover": {"lt": request.max_cloud_cover}}

        item_search = self.client.search(**params)
        records = [self._item_to_record(item) for item in item_search.items()]
        records.sort(key=lambda record: (record.datetime or "", record.item_id))
        return records

    def get_coverage(self, dataset: str) -> list[CollectionCoverage]:
        coverages: list[CollectionCoverage] = []
        for collection_id in self.resolve_collections(dataset):
            collection = self.client.get_collection(collection_id)
            if collection is None:
                raise ValueError(f"Collection {collection_id!r} was not found in Earth Search.")
            extent = collection.extent
            spatial_bboxes = getattr(extent.spatial, "bboxes", []) or []
            spatial_bbox = spatial_bboxes[0] if spatial_bboxes else None
            temporal_intervals_raw = getattr(extent.temporal, "intervals", []) or []
            temporal_intervals = [
                [_datetime_to_iso(start), _datetime_to_iso(end)]
                for start, end in temporal_intervals_raw
            ]
            coverages.append(
                CollectionCoverage.from_extent(
                    provider=self.name,
                    collection=collection_id,
                    spatial_bbox=spatial_bbox,
                    temporal_intervals=temporal_intervals,
                )
            )
        return coverages

    def get_item(self, collection_id: str, item_id: str) -> tuple[Any, Any]:
        collection = self.client.get_collection(collection_id)
        if collection is None:
            raise ValueError(f"Collection {collection_id!r} was not found in Earth Search.")
        item = collection.get_item(item_id)
        if item is None:
            raise ValueError(f"Item {item_id!r} was not found in collection {collection_id!r}.")
        return collection, item

    def inspect_scene_assets(self, collection_id: str, item_id: str) -> list[AssetSpec]:
        collection, item = self.get_item(collection_id, item_id)
        return asset_specs_from_item(provider_name=self.name, collection=collection, item=item)

    def _item_to_record(self, item: Any) -> SceneRecord:
        properties = getattr(item, "properties", {}) or {}
        collection_id = getattr(item, "collection_id", None) or properties.get("collection") or ""
        item_datetime = getattr(item, "datetime", None) or properties.get("datetime")
        cloud_cover = properties.get("eo:cloud_cover")
        if cloud_cover is not None:
            cloud_cover = float(cloud_cover)
        bbox_raw = getattr(item, "bbox", None)
        bbox = tuple(float(v) for v in bbox_raw) if bbox_raw and len(bbox_raw) == 4 else None
        geometry_raw = getattr(item, "geometry", None)
        geometry = dict(geometry_raw) if isinstance(geometry_raw, Mapping) else geometry_raw
        assets = getattr(item, "assets", {}) or {}
        return SceneRecord(
            provider=self.name,
            collection=str(collection_id),
            item_id=str(item.id),
            datetime=_datetime_to_iso(item_datetime),
            platform=properties.get("platform"),
            cloud_cover=cloud_cover,
            bbox=bbox,
            geometry=geometry,
            asset_keys=tuple(sorted(str(key) for key in assets.keys())),
        )
