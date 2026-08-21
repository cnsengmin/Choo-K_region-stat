# GeoReach

GeoReach is the planned source-access and normalization layer for Choo-K Region Stat.

## Responsibilities

- select an appropriate source backend for a requested layer/area/vintage
- fetch raw source data
- normalize geometry and schema
- validate coverage and basic quality
- record provenance
- expose source health information
- fall back only to explicitly registered alternatives

## Non-responsibilities

GeoReach does not own map rendering, chart styling, or final analytical interpretation.

## Planned package shape

```text
georeach/
├─ channels/
│  ├─ boundary/
│  ├─ population/
│  ├─ building/
│  ├─ parcel/
│  ├─ zoning/
│  ├─ road/
│  └─ terrain/
├─ registry/
├─ provenance/
├─ doctor/
├─ normalize/
└─ cache/
```

Implementation begins after official source verification and the reuse-first architecture spike.
