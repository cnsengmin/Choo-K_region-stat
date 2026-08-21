# Data Source Registry — Planning Document

> This document records intended source families. A source is not considered verified until its official endpoint, license/terms, schema, coverage, update cycle, and test request have been checked and entered in the machine-readable registry.

## Rules

1. Prefer authoritative national/local public sources.
2. Do not silently substitute an unofficial source for an authoritative one.
3. Keep source access separate from normalized layer schemas.
4. Record retrieval date and dataset vintage separately.
5. Record license/terms at layer/source level.
6. Preserve historical administrative-boundary versions when longitudinal analysis requires them.
7. Never commit API keys or restricted raw data.

## Planned baseline layers

| Layer family | Candidate provider/source family | MVP | Notes to verify |
|---|---|---:|---|
| Administrative boundaries | SGIS / national spatial-data sources | Yes | Historical boundary versions, codes, CRS |
| Population grids | SGIS / census grid products | Yes | 100m availability, vintage, age groups, disclosure rules |
| Buildings | Building-register / national building spatial APIs | Yes | footprint linkage, use, approval date, floors, height |
| Parcels / cadastral | National continuous cadastral products | Yes | license, refresh cycle, identifiers |
| Zoning / land use | National spatial planning / VWorld-type public sources | Yes | classification consistency and plan vintage |
| Roads | National/local road spatial data; OSM as clearly-labelled fallback where appropriate | Yes | authoritative hierarchy, topology |
| Terrain | NGII/national DEM products | Yes | resolution, redistribution terms, contour derivation |
| Green space | land-cover + park/green-space sources | Next | distinguish physical cover vs legal park/green designation |
| Transit | national/local subway and bus APIs | Next | stop/station IDs and service changes |
| Planning facilities | urban planning facility datasets | Next | municipality coverage and plan date |
| District-unit plans | urban planning datasets | Next | municipality coverage, geometry, effective dates |
| Businesses | census/business establishment products | Later | grid resolution, industry codes, temporal comparability |
| Floating population | local/open mobility products | Later | licensing and city-to-city comparability |
| Commercial districts | SGIS/local commercial data | Later | national baseline vs Seoul/local enrichment |

## Provenance fields

Each verified source registry entry should contain:

```yaml
id: example
provider: Example Provider
title: Example Dataset
layer_family: building
authority: authoritative
access:
  type: api
  endpoint: null
auth:
  required: true
coverage:
  spatial: nationwide
  temporal: null
update_cycle: null
source_crs: null
license:
  name: null
  url: null
preferred_rank: 1
last_verified: null
schema_mapping: {}
limitations: []
```

## Local enrichment

Local portals may provide richer data than the national baseline. These should be modeled as enrichment/override channels rather than making the application city-specific. Seoul is an obvious later test because of its rich open-data ecosystem; the initial functional pilot remains Anyang/Pyeongchon.

## Historical comparability

Longitudinal statistics require explicit treatment of:

- administrative-code changes
- boundary changes
- grid-system/version changes
- classification revisions
- source methodology revisions

The project should eventually maintain crosswalks rather than assuming same-name areas are spatially identical over time.
