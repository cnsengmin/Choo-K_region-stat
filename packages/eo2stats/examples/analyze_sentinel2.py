from eo2stats import analyze_sentinel2_scene, search_scenes

BBOX = (126.92, 37.35, 127.02, 37.43)

scenes = search_scenes(
    dataset="sentinel-2-l2a",
    start_date="2026-08-01",
    end_date="2026-08-31",
    bbox=BBOX,
    max_cloud_cover=20,
    limit=20,
)

if not scenes:
    raise SystemExit("No Sentinel-2 scenes found for the requested AOI/date range.")

scene = scenes[0]
results = analyze_sentinel2_scene(
    collection=scene.collection,
    item_id=scene.item_id,
    bbox_wgs84=BBOX,
    indices=("ndvi", "ndwi", "mndwi", "ndbi"),
    mask_policy="research-clear-v1",
)

print(f"Scene: {scene.item_id} ({scene.datetime})")
for name, result in results.items():
    print(name.upper())
    print("  summary:", result.summary.to_dict())
    print("  provenance:", result.provenance())
