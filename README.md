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

## eo2stats — Earth observation research layer

A reusable package is now being prototyped under [`packages/eo2stats`](packages/eo2stats/README.md).

Its purpose is to connect open satellite/environmental data to urban research while preserving the meaning of each variable's native spatial support.

The package separates three tasks:

```text
Earth observation
      ↓
physical urban-feature extraction
      ↓
guarded spatialization of administrative/social indicators
```

This is deliberately broader than a satellite downloader. The intended long-term interfaces are Python/CLI, MCP, QGIS and the web Atlas, all calling the same scientific core.

A core rule is that **row resolution is not information resolution**. A sigungu fiscal ratio copied to 100 m grid rows remains a sigungu-level contextual variable, while building coverage calculated from fine-scale geometry is genuinely a new grid-level measurement. See [`INDICATOR_SPATIALIZATION.md`](packages/eo2stats/docs/INDICATOR_SPATIALIZATION.md).

## Architecture principles

- **Source adapters, not one-off download scripts.** Each layer is represented by a `GeoChannel` with preferred and fallback sources.
- **Reproducible provenance.** Every derived layer records where it came from, its reference date, license, CRS, spatial support, and transformations.
- **Fail visibly.** A `geo-doctor` concept reports source/API/cache health rather than silently returning stale or missing data.
- **One normalized pipeline, multiple outputs.** Maps, statistics, diagrams, MCP tools and 3D views should not maintain separate copies of the same source data.
- **Repo-first reuse.** Mature open-source components are evaluated before custom implementation.
- **National scalability.** Local exceptions are adapters/configuration, not hard-coded assumptions in the core.
- **No false precision.** Administrative/social indicators are not automatically downscaled simply because a finer grid exists.

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
- EO discovery: STAC / pystac-client
- EO time series: odc-stac or stackstac
- Change of support: PySAL/tobler where conceptually valid
- AI feature extraction: adapters to GeoAI/segment-geospatial and task-specific models

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
├─ packages/
│  └─ eo2stats/
│     ├─ README.md
│     ├─ pyproject.toml
│     ├─ docs/
│     │  ├─ ARCHITECTURE.md
│     │  ├─ INDICATOR_SPATIALIZATION.md
│     │  ├─ RELATED_PROJECTS.md
│     │  └─ satellite-data/
│     ├─ src/eo2stats/
│     └─ tests/
└─ .gitignore
```

## Reference inspiration

The data-source resilience idea is inspired by Agent-Reach's channel/backend approach, adapted here for geospatial public-data sources. Choo-K Region Stat is a separate project and will not assume that Agent-Reach itself provides GIS functionality.

## Status

**Phase 0/1 — repository architecture, EO data catalog, spatial-support semantics and first retrieval prototype.**

See `docs/ROADMAP.md`, `docs/REUSE_RESEARCH.md`, and `packages/eo2stats/README.md` before implementation.
