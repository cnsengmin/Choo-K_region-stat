from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class AssetSpec:
    provider: str
    collection: str
    item_id: str
    key: str
    href: str
    media_type: str | None
    roles: tuple[str, ...]
    title: str | None
    gsd: float | None
    data_type: str | None
    nodata: float | int | None
    unit: str | None
    scale: float | None
    offset: float | None
    kind: str
    is_cog: bool

    def to_dict(self) -> dict[str, Any]:
        row = asdict(self)
        row["roles"] = list(self.roles)
        return row


@dataclass(slots=True)
class RasterWindowResult:
    asset: AssetSpec
    data: Any
    crs: str
    transform: tuple[float, ...]
    bbox_wgs84: tuple[float, float, float, float]
    scale_applied: bool


def _asset_kind(key: str, roles: tuple[str, ...]) -> str:
    role_set = set(roles)
    if "metadata" in role_set:
        return "metadata"
    if "visual" in role_set or "overview" in role_set or "thumbnail" in role_set:
        return "visual"
    if "reflectance" in role_set:
        return "reflectance"
    if key.lower() in {"scl", "qa_pixel", "qa_radsat"}:
        return "classification"
    if "cloud" in role_set or "snow-ice" in role_set:
        return "probability"
    return "measurement"


def asset_specs_from_item(*, provider_name: str, collection: Any, item: Any) -> list[AssetSpec]:
    item_assets_fallback: Mapping[str, Any] = getattr(collection, "extra_fields", {}).get("item_assets", {}) or {}
    specs: list[AssetSpec] = []
    for key, asset in (getattr(item, "assets", {}) or {}).items():
        fallback = dict(item_assets_fallback.get(key, {}) or {})
        extra = dict(getattr(asset, "extra_fields", {}) or {})
        metadata = {**fallback, **extra}
        raster_bands = metadata.get("raster:bands") or []
        first_band = raster_bands[0] if raster_bands and isinstance(raster_bands[0], Mapping) else {}
        roles = tuple(getattr(asset, "roles", None) or metadata.get("roles") or ())
        media_type = getattr(asset, "media_type", None) or metadata.get("type")
        title = getattr(asset, "title", None) or metadata.get("title")
        href = str(getattr(asset, "href", ""))
        gsd = metadata.get("gsd")
        if gsd is not None:
            gsd = float(gsd)
        scale = first_band.get("scale")
        offset = first_band.get("offset")
        if scale is not None:
            scale = float(scale)
        if offset is not None:
            offset = float(offset)
        nodata = first_band.get("nodata")
        is_cog = bool(media_type and "cloud-optimized" in media_type.lower())
        specs.append(
            AssetSpec(
                provider=provider_name,
                collection=str(getattr(item, "collection_id", None) or getattr(collection, "id", "")),
                item_id=str(item.id),
                key=str(key),
                href=href,
                media_type=media_type,
                roles=roles,
                title=title,
                gsd=gsd,
                data_type=first_band.get("data_type"),
                nodata=nodata,
                unit=first_band.get("unit"),
                scale=scale,
                offset=offset,
                kind=_asset_kind(str(key), roles),
                is_cog=is_cog,
            )
        )
    return sorted(specs, key=lambda spec: spec.key)
