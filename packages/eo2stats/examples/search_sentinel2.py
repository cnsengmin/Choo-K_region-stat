"""Small Sentinel-2 discovery smoke test.

The bbox is an approximate Anyang/Pyeongchon window for development only.
Use an authoritative study-area geometry for research.
"""

from eo2stats import get_dataset_coverage, search_scenes


BBOX = (126.92, 37.35, 127.02, 37.43)


if __name__ == "__main__":
    coverage = get_dataset_coverage("sentinel-2-l2a")
    for collection in coverage:
        print(collection)

    scenes = search_scenes(
        dataset="sentinel-2-l2a",
        start_date="2026-08-01",
        end_date="2026-08-31",
        bbox=BBOX,
        max_cloud_cover=20,
        limit=20,
    )

    for scene in scenes:
        print(scene.to_dict())
