from __future__ import annotations

from .models import IndicatorSpec, PolicyDecision, QuantityType, SupportType, TransformMethod


def evaluate_spatialization(
    indicator: IndicatorSpec,
    method: TransformMethod,
) -> PolicyDecision:
    """Evaluate whether a proposed change-of-support operation is conceptually valid.

    This function does not perform interpolation. It prevents downstream adapters
    (CLI, MCP, QGIS) from silently manufacturing fine-scale precision.
    """

    if method is TransformMethod.CONTEXTUAL_JOIN:
        return PolicyDecision(
            allowed=True,
            method=method,
            preserves_native_support=True,
            creates_target_scale_estimate=False,
            reason=(
                "The value may be attached to target rows as contextual information, "
                "but its information support remains the native support."
            ),
            warnings=(
                "Do not label the joined value as a target-scale estimate.",
                "Use multilevel/cluster-aware inference when the source support is administrative.",
            ),
        )

    if indicator.native_support_type is SupportType.REGULATORY_POLYGON:
        if method is TransformMethod.INTERSECTION:
            return PolicyDecision(
                allowed=True,
                method=method,
                preserves_native_support=False,
                creates_target_scale_estimate=False,
                reason="Regulatory boundaries should be transferred by geometric overlap/share.",
            )
        return PolicyDecision(
            allowed=False,
            method=method,
            preserves_native_support=True,
            creates_target_scale_estimate=False,
            reason="A legal/regulatory category should not be numerically interpolated.",
        )

    if method in {
        TransformMethod.AREA_WEIGHTED,
        TransformMethod.DASYMETRIC,
        TransformMethod.MODEL_DISAGGREGATION,
    }:
        if indicator.quantity_type is not QuantityType.EXTENSIVE:
            return PolicyDecision(
                allowed=False,
                method=method,
                preserves_native_support=True,
                creates_target_scale_estimate=False,
                reason=(
                    "Spatial redistribution methods are reserved for additive totals/counts. "
                    "Rates, ratios and means cannot be treated as mass."
                ),
            )

        warnings: tuple[str, ...] = ()
        if method is TransformMethod.AREA_WEIGHTED:
            warnings = (
                "Area weighting assumes uniform density within the source polygon.",
                "Consider dasymetric constraints when built/inhabited areas are known.",
            )

        return PolicyDecision(
            allowed=True,
            method=method,
            preserves_native_support=False,
            creates_target_scale_estimate=True,
            reason="An extensive total may be redistributed under an explicit conservation rule.",
            warnings=warnings,
        )

    if method is TransformMethod.RECOMPUTE_RATE:
        has_components = bool(
            indicator.numerator_indicator_id and indicator.denominator_indicator_id
        )
        return PolicyDecision(
            allowed=has_components and indicator.quantity_type is QuantityType.INTENSIVE,
            method=method,
            preserves_native_support=False,
            creates_target_scale_estimate=has_components,
            reason=(
                "Rates should be recomputed from spatialized numerator and denominator."
                if has_components
                else "Numerator and denominator metadata are required to reconstruct a rate."
            ),
        )

    if method in {TransformMethod.ZONAL_STATS, TransformMethod.AGGREGATE}:
        allowed = indicator.quantity_type in {
            QuantityType.CONTINUOUS_SURFACE,
            QuantityType.GEOMETRY,
            QuantityType.EXTENSIVE,
        }
        return PolicyDecision(
            allowed=allowed,
            method=method,
            preserves_native_support=False,
            creates_target_scale_estimate=False,
            reason=(
                "Aggregation is valid when the target statistic is explicitly defined from "
                "fine-scale observations or geometry."
                if allowed
                else "This variable requires a more specific support transformation."
            ),
        )

    return PolicyDecision(
        allowed=False,
        method=method,
        preserves_native_support=True,
        creates_target_scale_estimate=False,
        reason="No approved rule exists for this indicator/method combination.",
    )
