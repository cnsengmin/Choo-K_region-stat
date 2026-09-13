import numpy as np

from eo2stats.sentinel2 import IndexSummary, SpectralIndexResult
from eo2stats.temporal import (
    CompositePolicy,
    TemporalObservation,
    build_temporal_composites,
    composite_observations,
    temporal_group_key,
)


def _result(
    item_id: str,
    data,
    *,
    valid_ratio: float = 1.0,
    index: str = "ndvi",
    gsd: float = 10.0,
    transform=(10.0, 0.0, 0.0, 0.0, -10.0, 20.0),
    mask_policy: str = "research-clear-v1",
):
    values = np.ma.asarray(data, dtype=np.float32)
    n_total = int(values.size)
    n_valid = int(values.count())
    summary = IndexSummary(
        n_total_pixels=n_total,
        n_valid_pixels=n_valid,
        valid_pixel_ratio=valid_ratio,
        masked_pixel_ratio=1.0 - valid_ratio,
        mean=float(values.mean()) if n_valid else None,
        median=float(np.ma.median(values)) if n_valid else None,
        std=float(values.std()) if n_valid else None,
        minimum=float(values.min()) if n_valid else None,
        maximum=float(values.max()) if n_valid else None,
    )
    return SpectralIndexResult(
        name=index,
        data=values,
        crs="EPSG:32652",
        transform=transform,
        target_gsd=gsd,
        qa_gsd=20.0,
        mask_policy=mask_policy,
        source_assets=("nir", "red", "scl"),
        provider="earth-search",
        collection="sentinel-2-c1-l2a",
        item_id=item_id,
        scale_applied={"nir": True, "red": True, "scl": False},
        summary=summary,
    )


def test_temporal_group_keys_include_cross_year_djf():
    assert temporal_group_key("2026-08-03T01:00:00Z") == "2026-08"
    assert temporal_group_key("2025-12-15T01:00:00Z", "seasonal") == "2026-DJF"
    assert temporal_group_key("2026-01-15T01:00:00Z", "seasonal") == "2026-DJF"
    assert temporal_group_key("2026-06-15T01:00:00Z", "seasonal") == "2026-JJA"


def test_median_composite_preserves_missing_and_counts_observations():
    first = _result(
        "a",
        np.ma.array([[0.2, 0.4], [0.6, 0.8]], mask=[[0, 0], [0, 1]]),
        valid_ratio=0.75,
    )
    second = _result(
        "b",
        np.ma.array([[0.4, 0.2], [0.8, 1.0]], mask=[[0, 1], [0, 0]]),
        valid_ratio=0.75,
    )
    result = composite_observations(
        [
            TemporalObservation("2026-08-03T00:00:00Z", first),
            TemporalObservation("2026-08-20T00:00:00Z", second),
        ],
        period_key="2026-08",
    )
    np.testing.assert_allclose(
        result.data.filled(np.nan),
        np.array([[0.3, 0.4], [0.7, 1.0]], dtype=np.float32),
        equal_nan=True,
    )
    np.testing.assert_array_equal(result.n_observations, [[2, 1], [2, 1]])
    assert result.summary.valid_area_ratio == 1.0
    assert result.summary.mean_observations == 1.5


def test_min_observations_masks_low_support_pixels():
    first = _result("a", np.ma.array([[0.2, 0.4]], mask=[[0, 0]]))
    second = _result("b", np.ma.array([[0.4, 0.2]], mask=[[0, 1]]), valid_ratio=0.5)
    result = composite_observations(
        [
            TemporalObservation("2026-08-03T00:00:00Z", first),
            TemporalObservation("2026-08-20T00:00:00Z", second),
        ],
        period_key="2026-08",
        policy=CompositePolicy(min_observations=2),
    )
    assert result.data.mask.tolist() == [[False, True]]
    assert result.summary.n_valid_pixels == 1


def test_scene_quality_filter_is_explicit_and_recorded():
    good = _result("good", [[0.2, 0.4]], valid_ratio=0.8)
    poor = _result("poor", [[0.9, 0.9]], valid_ratio=0.2)
    result = composite_observations(
        [
            TemporalObservation("2026-08-03T00:00:00Z", good),
            TemporalObservation("2026-08-20T00:00:00Z", poor),
        ],
        period_key="2026-08",
        policy=CompositePolicy(min_scene_valid_ratio=0.5),
    )
    assert result.source_item_ids == ("good",)
    assert result.rejected_item_ids == ("poor",)
    assert result.summary.usable_scene_count == 1
    assert result.summary.rejected_scene_count == 1


def test_build_monthly_composites_uses_acquisition_time():
    july = _result("july", [[0.1]])
    august_a = _result("aug-a", [[0.2]])
    august_b = _result("aug-b", [[0.4]])
    output = build_temporal_composites(
        [
            TemporalObservation("2026-07-31T23:00:00Z", july),
            TemporalObservation("2026-08-01T01:00:00Z", august_a),
            TemporalObservation("2026-08-12T01:00:00Z", august_b),
        ]
    )
    assert list(output) == ["2026-07", "2026-08"]
    assert output["2026-08"].source_item_ids == ("aug-a", "aug-b")
    assert np.isclose(float(output["2026-08"].data[0, 0]), 0.3)


def test_composite_rejects_mixed_index_or_mask_policy():
    ndvi = _result("a", [[0.2]], index="ndvi")
    ndbi = _result("b", [[0.3]], index="ndbi", gsd=20.0, transform=(20, 0, 0, 0, -20, 20))
    with np.testing.assert_raises(ValueError):
        composite_observations(
            [
                TemporalObservation("2026-08-01", ndvi),
                TemporalObservation("2026-08-02", ndbi),
            ],
            period_key="2026-08",
        )

    strict = _result("c", [[0.3]], mask_policy="research-strict-v1")
    with np.testing.assert_raises(ValueError):
        composite_observations(
            [
                TemporalObservation("2026-08-01", ndvi),
                TemporalObservation("2026-08-02", strict),
            ],
            period_key="2026-08",
        )
