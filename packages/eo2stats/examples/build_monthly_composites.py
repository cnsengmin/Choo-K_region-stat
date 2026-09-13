from eo2stats import (
    CompositePolicy,
    TemporalObservation,
    analyze_sentinel2_scene,
    build_temporal_composites,
    search_scenes,
)

BBOX = (126.92, 37.35, 127.02, 37.43)

scenes = search_scenes(
    dataset="sentinel-2-l2a",
    start_date="2026-06-01",
    end_date="2026-08-31",
    bbox=BBOX,
    max_cloud_cover=60,
)

observations = []
for scene in scenes:
    if scene.datetime is None:
        continue
    result = analyze_sentinel2_scene(
        collection=scene.collection,
        item_id=scene.item_id,
        bbox_wgs84=BBOX,
        indices=("ndvi",),
        mask_policy="research-clear-v1",
    )["ndvi"]
    observations.append(
        TemporalObservation(
            acquisition_datetime=scene.datetime,
            result=result,
        )
    )

monthly = build_temporal_composites(
    observations,
    frequency="monthly",
    policy=CompositePolicy(
        method="median",
        min_scene_valid_ratio=0.30,
        min_observations=1,
    ),
)

for period, composite in monthly.items():
    print(period)
    print(composite.summary.to_dict())
    print(composite.provenance())
