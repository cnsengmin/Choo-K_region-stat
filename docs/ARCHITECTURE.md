# Architecture

## 1. Product boundary

Choo-K Region Stat is not primarily a GIS desktop replacement. It is a regional-data access and interpretation layer for Korea.

A user selects a location or administrative unit. The system resolves the area, obtains the required spatial/statistical layers, normalizes them, computes indicators, and exposes the result through map, statistics, diagram, and 2.5D/3D views.

## 2. High-level flow

```text
User / Agent
    |
Area Resolver
(address, click, admin unit, radius, bbox)
    |
Spatial Orchestrator
    |
GeoReach source adapters
    |
normalize + validate + provenance
    |
GeoParquet / PMTiles / PostGIS / cache
    |
+-----------+------------+-------------+
| Map View  | Statistics | Diagram/3D  |
+-----------+------------+-------------+
```

## 3. GeoReach

`GeoReach` is the internal source-adapter layer. The design borrows the useful idea of ordered/fallback backends from Agent-Reach but applies it to Korean geospatial/statistical sources.

Conceptual interface:

```python
class GeoChannel:
    name: str
    layers: list[str]

    def can_handle(self, layer, area): ...
    def check(self): ...
    def fetch(self, area, vintage=None): ...
    def normalize(self, raw): ...
    def validate(self, normalized): ...
    def provenance(self): ...
```

A channel may expose multiple ordered backends:

```text
PopulationChannel
  1. authoritative API
  2. authoritative bulk download
  3. verified local cache
```

Fallback does not erase provenance: the selected backend is always recorded.

## 4. Core channels for MVP

- `BoundaryChannel`
- `PopulationChannel`
- `BuildingChannel`
- `ParcelChannel`
- `ZoningChannel`
- `RoadChannel`
- `TerrainChannel`

Next wave:

- `TransitChannel`
- `GreenSpaceChannel`
- `PlanningFacilityChannel`
- `DistrictPlanChannel`
- `BusinessChannel`
- `CommercialAreaChannel`
- `FloatingPopulationChannel`

## 5. Canonical data model

Each normalized dataset should carry at least:

```text
layer_id
feature_id
geometry
source_id
source_record_id (when available)
vintage
retrieved_at
source_crs
canonical_crs
license_id
processing_version
quality_flags
```

Domain-specific fields remain in layer schemas. The core metadata above is never optional for persisted/derived outputs.

## 6. CRS policy

Do not force every computation into web mercator.

- Preserve source CRS in provenance.
- Use an appropriate Korean projected CRS for metric analysis.
- Transform to EPSG:4326/3857 only at delivery/render boundaries where needed.
- Store transformation details for reproducibility.

Exact canonical analytical CRS will be selected after testing source compatibility and national coverage.

## 7. Provenance registry

Every source must have a registry entry with:

- source owner/provider
- source title
- access method
- authoritative/public status
- spatial coverage
- temporal coverage and update cycle
- source CRS
- license/terms
- authentication requirements
- preferred/fallback rank
- schema mapping
- last verified date
- known limitations

No production source should exist only as an undocumented URL in application code.

## 8. geo-doctor

`geo-doctor` will test operational health rather than only configuration presence.

Example output:

```text
building      OK      authoritative API reachable
parcel        OK      bulk fallback available
population    WARN    API unavailable; verified cache selected
terrain       OK      local DEM tile coverage present
zoning        FAIL    no valid backend for requested area
```

Checks should distinguish:

- configuration error
- authentication error
- upstream outage
- coverage gap
- schema change
- stale cache
- license/terms uncertainty

## 9. Derived analytics

Initial derived layers:

- population density / age-group composition
- building age
- high/low-rise classes
- building-use classes
- road density
- block polygons
- KDE/density surfaces
- terrain contours

Future modules can add accessibility (service area, OD matrix, GA2SFCA), commercial activity, redevelopment indicators, and longitudinal change.

## 10. Rendering

### Map
MapLibre GL JS is the default candidate for basemap/vector interaction.

### Analytical overlays
Deck.gl is the default candidate for grids, density, extrusion, and larger analytical layers.

### 2.5D / 3D
Start with building extrusion and terrain. Use Three.js only for scenes that need custom exploded-layer/axonometric behavior. Do not introduce Cesium until a national 3D requirement justifies it.

### Diagram generator
A diagram is a styled transformation of normalized data, not a separately downloaded dataset. Candidate presets:

- Buildings
- Building Use
- Building Age
- High Buildings
- Low-rise
- Zoning
- Green Spaces
- District Unit Plan
- Planned Facilities
- Roads
- Subway & Bus
- City Block
- Density
- Terrain
- Cadastral

## 11. Export

Target export formats:

- PNG
- SVG
- CSV
- GeoJSON
- GeoPackage (preferred over Shapefile when possible)
- GLB for 3D
- PDF report at a later stage

Every export should be able to include or accompany a machine-readable provenance manifest.

## 12. Scalability rule

Pilot-area shortcuts must not leak into core contracts. Local government datasets can override or enrich national sources through adapters, but the core application must continue to work with national baseline sources.
