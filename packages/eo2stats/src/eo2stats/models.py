from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class SupportType(StrEnum):
    RASTER_PIXEL = "raster_pixel"
    GRID = "grid"
    POINT = "point"
    BUILDING = "building"
    PARCEL = "parcel"
    BLOCK = "block"
    NETWORK = "network"
    REGULATORY_POLYGON = "regulatory_polygon"
    ADMINISTRATIVE_POLYGON = "administrative_polygon"
    CUSTOM_POLYGON = "custom_polygon"


class QuantityType(StrEnum):
    EXTENSIVE = "extensive"  # totals/counts; additive over space
    INTENSIVE = "intensive"  # rates/ratios/means; not additive
    CATEGORICAL = "categorical"
    CONTINUOUS_SURFACE = "continuous_surface"
    GEOMETRY = "geometry"


class EvidenceType(StrEnum):
    OBSERVED = "observed"
    DERIVED = "derived"
    ESTIMATED = "estimated"
    CONTEXTUAL = "contextual"


class TransformMethod(StrEnum):
    ZONAL_STATS = "zonal_stats"
    AGGREGATE = "aggregate"
    INTERSECTION = "intersection"
    CONTEXTUAL_JOIN = "contextual_join"
    AREA_WEIGHTED = "area_weighted"
    DASYMETRIC = "dasymetric"
    MODEL_DISAGGREGATION = "model_disaggregation"
    RECOMPUTE_RATE = "recompute_rate"


@dataclass(slots=True)
class IndicatorSpec:
    indicator_id: str
    native_support_type: SupportType
    quantity_type: QuantityType
    evidence_type: EvidenceType
    native_support_level: str | None = None
    temporal_support: str | None = None
    unit: str | None = None
    mass_preserving_required: bool = False
    numerator_indicator_id: str | None = None
    denominator_indicator_id: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True)
class PolicyDecision:
    allowed: bool
    method: TransformMethod
    preserves_native_support: bool
    creates_target_scale_estimate: bool
    reason: str
    warnings: tuple[str, ...] = ()
