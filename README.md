# Choo-K Region Stat

Korea regional statistics, spatial data, urban analytics, and automated urban-diagram platform.

## Vision

**Click a place in Korea and understand the region.**

Choo-K Region Stat aims to unify fragmented Korean public geospatial/statistical data behind a common interface and provide four views over the same normalized data pipeline:

1. **Map** — browse interoperable national and local spatial layers.
2. **Statistics** — inspect population, business, accessibility, land-use, and urban-form indicators.
3. **Diagram** — generate publication-ready site/urban diagrams automatically.
4. **2.5D / 3D** — inspect buildings, terrain, roads, green space, water, and other layers spatially.

The long-term goal is national coverage. Development starts with a small Anyang/Pyeongchon pilot area and expands only after the data-source and provenance pipeline is stable.

## MVP

The first MVP focuses on a selected area in Anyang/Pyeongchon and supports:

- Buildings and building footprints
- Building use
- Building age
- High-rise / low-rise classification
- Parcels / cadastral data
- Zoning
- Roads
- Terrain / contours
- Population grid integration
- Source, vintage, license, CRS, and processing provenance for every layer

Later diagram modules will add green space, district-unit plans, planned facilities, subway/bus, city blocks, density, and additional regional-statistics layers.

## Architecture principles

- **Source adapters, not one-off download scripts.** Each layer is represented by a `GeoChannel` with preferred and fallback sources.
- **Reproducible provenance.** Every derived layer records where it came from, its reference date, license, CRS, and transformations.
- **Fail visibly.** A `geo-doctor` concept reports source/API/cache health rather than silently returning stale or missing data.
- **One normalized pipeline, multiple outputs.** Maps, statistics, diagrams, and 3D views should not maintain separate copies of the same source data.
- **Repo-first reuse.** Mature open-source components are evaluated before custom implementation.
- **National scalability.** Local exceptions are adapters/configuration, not hard-coded assumptions in the core.

## Candidate technology stack

The stack is intentionally provisional until the architecture spike is complete.

- Web: React / TypeScript
- 2D map: MapLibre GL JS
- Analytical overlays: deck.gl
- Browser spatial analytics: DuckDB-WASM Spatial where appropriate
- Server spatial store: PostGIS when national-scale persistence/querying is required
- Static/vector delivery: PMTiles / GeoParquet
- 2.5D/3D diagrams: MapLibre/deck.gl first; Three.js for exploded/diagram scenes
- API/data processing: Python

## Repository layout

```text
Choo-K_region-stat/
├─ README.md
├─ docs/
│  ├─ ARCHITECTURE.md
│  ├─ DATA_SOURCES.md
│  ├─ REUSE_RESEARCH.md
│  └─ ROADMAP.md
├─ georeach/
│  ├─ README.md
│  └─ registry/
│     └─ sources.example.yaml
└─ .gitignore
```

Application code will be added only after the architecture/reuse spike chooses the implementation baseline.

## Reference inspiration

The data-source resilience idea is inspired by Agent-Reach's channel/backend approach, adapted here for geospatial public-data sources. Choo-K Region Stat is a separate project and will not assume that Agent-Reach itself provides GIS functionality.

## Status

**Phase 0 — repository initialization and architecture/reuse research.**

See `docs/ROADMAP.md` and `docs/REUSE_RESEARCH.md` before implementation.
