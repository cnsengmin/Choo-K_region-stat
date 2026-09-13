from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from eo2stats.providers.earth_search import EarthSearchProvider
from eo2stats.scenes import SceneSearchRequest
from eo2stats.search import search_scenes


class FakeItemSearch:
    def __init__(self, items):
        self._items = items

    def items(self):
        return iter(self._items)


class FakeClient:
    def __init__(self, items=None, collections=None):
        self.items = items or []
        self.collections = collections or {}
        self.last_search = None

    def search(self, **kwargs):
        self.last_search = kwargs
        return FakeItemSearch(self.items)

    def get_collection(self, collection_id):
        return self.collections[collection_id]


class FakeItem:
    def __init__(self):
        self.id = "S2_TEST"
        self.collection_id = "sentinel-2-c1-l2a"
        self.datetime = datetime(2026, 9, 1, 2, 3, tzinfo=timezone.utc)
        self.properties = {"platform": "sentinel-2a", "eo:cloud_cover": 7.5}
        self.bbox = [126.8, 37.3, 127.1, 37.5]
        self.geometry = {"type": "Polygon", "coordinates": []}
        self.assets = {"nir": object(), "red": object(), "scl": object()}


def test_sentinel_alias_searches_both_current_earth_search_collections():
    client = FakeClient(items=[FakeItem()])
    provider = EarthSearchProvider(client=client)

    result = search_scenes(
        dataset="sentinel-2-l2a",
        start_date="2026-09-01",
        end_date="2026-09-10",
        bbox=(126.8, 37.3, 127.1, 37.5),
        max_cloud_cover=20,
        limit=100,
        provider=provider,
    )

    assert client.last_search["collections"] == [
        "sentinel-2-pre-c1-l2a",
        "sentinel-2-c1-l2a",
    ]
    assert client.last_search["query"] == {"eo:cloud_cover": {"lt": 20}}
    assert client.last_search["max_items"] == 100
    assert result[0].item_id == "S2_TEST"
    assert result[0].asset_keys == ("nir", "red", "scl")
    assert result[0].cloud_cover == 7.5


def test_geojson_feature_is_normalized_to_geometry():
    client = FakeClient()
    provider = EarthSearchProvider(client=client)
    feature = {
        "type": "Feature",
        "properties": {"name": "AOI"},
        "geometry": {"type": "Polygon", "coordinates": []},
    }

    provider.search_scenes(
        SceneSearchRequest(
            dataset="sentinel-2-l2a",
            start_date="2026-01-01",
            end_date="2026-01-31",
            intersects=feature,
        )
    )

    assert client.last_search["intersects"] == feature["geometry"]


def test_request_requires_exactly_one_spatial_filter():
    with pytest.raises(ValueError):
        SceneSearchRequest(dataset="sentinel-2-l2a", start_date="2026-01-01", end_date="2026-01-02")

    with pytest.raises(ValueError):
        SceneSearchRequest(
            dataset="sentinel-2-l2a",
            start_date="2026-01-01",
            end_date="2026-01-02",
            bbox=(0, 0, 1, 1),
            intersects={"type": "Polygon", "coordinates": []},
        )


def test_coverage_is_read_from_collection_metadata():
    extent = SimpleNamespace(
        spatial=SimpleNamespace(bboxes=[[-180, -90, 180, 90]]),
        temporal=SimpleNamespace(
            intervals=[
                [datetime(2015, 6, 27, tzinfo=timezone.utc), datetime(2022, 1, 1, tzinfo=timezone.utc)]
            ]
        ),
    )
    collections = {
        "sentinel-2-pre-c1-l2a": SimpleNamespace(extent=extent),
        "sentinel-2-c1-l2a": SimpleNamespace(extent=extent),
    }
    provider = EarthSearchProvider(client=FakeClient(collections=collections))

    coverage = provider.get_coverage("sentinel-2-l2a")

    assert len(coverage) == 2
    assert coverage[0].spatial_bbox == (-180.0, -90.0, 180.0, 90.0)
    assert coverage[0].temporal_intervals[0][0].startswith("2015-06-27")
