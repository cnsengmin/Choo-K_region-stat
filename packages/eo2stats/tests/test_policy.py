from eo2stats import (
    EvidenceType,
    IndicatorSpec,
    QuantityType,
    SupportType,
    TransformMethod,
    evaluate_spatialization,
)


def test_fiscal_ratio_cannot_be_area_weighted():
    spec = IndicatorSpec(
        indicator_id="fiscal_self_reliance_ratio",
        native_support_type=SupportType.ADMINISTRATIVE_POLYGON,
        native_support_level="sigungu",
        quantity_type=QuantityType.INTENSIVE,
        evidence_type=EvidenceType.OBSERVED,
        unit="percent",
    )

    decision = evaluate_spatialization(spec, TransformMethod.AREA_WEIGHTED)

    assert decision.allowed is False
    assert decision.creates_target_scale_estimate is False


def test_population_total_can_be_dasymetrically_disaggregated():
    spec = IndicatorSpec(
        indicator_id="population_total",
        native_support_type=SupportType.ADMINISTRATIVE_POLYGON,
        native_support_level="eupmyeondong",
        quantity_type=QuantityType.EXTENSIVE,
        evidence_type=EvidenceType.OBSERVED,
        unit="persons",
        mass_preserving_required=True,
    )

    decision = evaluate_spatialization(spec, TransformMethod.DASYMETRIC)

    assert decision.allowed is True
    assert decision.creates_target_scale_estimate is True


def test_zoning_uses_geometric_intersection():
    spec = IndicatorSpec(
        indicator_id="zoning_type",
        native_support_type=SupportType.REGULATORY_POLYGON,
        quantity_type=QuantityType.CATEGORICAL,
        evidence_type=EvidenceType.OBSERVED,
    )

    assert evaluate_spatialization(spec, TransformMethod.INTERSECTION).allowed is True
    assert evaluate_spatialization(spec, TransformMethod.AREA_WEIGHTED).allowed is False


def test_contextual_join_does_not_claim_target_scale_information():
    spec = IndicatorSpec(
        indicator_id="municipal_debt_ratio",
        native_support_type=SupportType.ADMINISTRATIVE_POLYGON,
        native_support_level="sigungu",
        quantity_type=QuantityType.INTENSIVE,
        evidence_type=EvidenceType.CONTEXTUAL,
    )

    decision = evaluate_spatialization(spec, TransformMethod.CONTEXTUAL_JOIN)

    assert decision.allowed is True
    assert decision.preserves_native_support is True
    assert decision.creates_target_scale_estimate is False
