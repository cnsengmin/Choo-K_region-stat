# Reuse-first Research Gate

Before substantial implementation, inspect mature open-source repositories and document the decision.

This prevents rebuilding solved GIS infrastructure and keeps the project focused on Korean data normalization, provenance, analytics, and user experience.

## Required decision record

For each major subsystem, record:

1. **Candidate repositories**
2. **Why selected / rejected**
3. **Files/modules we expect to adapt or integrate**
4. **How runnability will be verified**

A repository is not selected only because it has many stars. Check license, maintenance, architecture fit, data model, bundle/runtime cost, and ability to test locally.

## Initial candidates

### Map rendering

- MapLibre GL JS
- deck.gl

Research questions:

- vector-tile performance
- large grid rendering
- feature-state/filter interaction
- extrusion support
- export limitations

### Spatial data/query

- DuckDB + spatial extension / DuckDB-WASM where browser-side analytics is useful
- PostGIS for persistent national-scale server queries
- GeoParquet for analytical interchange
- PMTiles for static vector delivery

### 3D / diagram

- deck.gl polygon/column/terrain-related layers
- Three.js for custom exploded axonometric scenes

Research questions:

- can a single normalized geometry model feed both map and diagram?
- SVG export strategy
- GLB export strategy
- terrain + building alignment

### Source resilience / monitoring

- Agent-Reach (Panniantong/Agent-Reach) as a design reference for ordered backends and health checks

Decision boundary:

Agent-Reach is **not** the GIS engine. Reuse its architectural ideas or integrate it for external-source monitoring only where that is cleaner than duplicating functionality.

## First architecture spike deliverable

Before UI implementation, produce a short decision matrix for the candidates above and a runnable proof of concept that:

1. loads one pilot-area polygon/bbox;
2. loads at least one building layer and one population/statistical layer;
3. renders them on a map;
4. derives one diagram classification;
5. emits provenance metadata;
6. demonstrates one fallback source or cached fallback;
7. documents exact commands used to reproduce the run.
