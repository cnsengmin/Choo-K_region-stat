# Roadmap

## Phase 0 — Foundation

- [x] Create repository
- [x] Define product vision and MVP boundary
- [x] Define GeoReach/source-adapter concept
- [x] Define provenance policy
- [x] Add reuse-first research gate
- [ ] Verify official baseline sources and licenses
- [ ] Select exact pilot bbox/administrative unit in Anyang/Pyeongchon
- [ ] Complete architecture decision matrix

**Exit criterion:** sources and technical baseline are documented well enough to build without embedding undocumented assumptions.

## Phase 1 — Pilot data pipeline

Implement initial channels:

- [ ] BoundaryChannel
- [ ] BuildingChannel
- [ ] PopulationChannel
- [ ] ParcelChannel
- [ ] ZoningChannel
- [ ] RoadChannel
- [ ] TerrainChannel

Also:

- [ ] canonical metadata schema
- [ ] provenance manifest
- [ ] local cache strategy
- [ ] `geo-doctor` health checks
- [ ] reproducible pilot-area ingest command

**Exit criterion:** one command can assemble the pilot-area baseline dataset with provenance.

## Phase 2 — Map + first diagrams

- [ ] interactive map
- [ ] click / address / bbox / radius area selection
- [ ] Buildings
- [ ] Building Use
- [ ] Building Age
- [ ] High Buildings
- [ ] Low-rise
- [ ] Zoning
- [ ] Roads
- [ ] Terrain
- [ ] Cadastral
- [ ] population grid overlay

**Exit criterion:** a user can select the pilot area and generate the first diagram set from the same underlying data.

## Phase 3 — 2.5D / 3D

- [ ] building extrusion
- [ ] terrain
- [ ] roads / green / water layers
- [ ] exploded layer view
- [ ] camera presets / axonometric mode
- [ ] PNG export
- [ ] investigate SVG / GLB export

## Phase 4 — Full 15-diagram family

- [ ] Green Spaces
- [ ] District Unit Plan
- [ ] Planned Facilities
- [ ] Subway & Bus
- [ ] City Block
- [ ] Density / KDE
- [ ] styling presets and legends

## Phase 5 — Regional-statistics analytics

- [ ] age-group population
- [ ] longitudinal population change
- [ ] businesses / employment
- [ ] commercial activity
- [ ] transit accessibility
- [ ] green-space accessibility
- [ ] urban-form metrics
- [ ] accessibility methods including service areas / OD / GA2SFCA where appropriate

## Phase 6 — Temporal and national expansion

- [ ] historical boundary/version crosswalks
- [ ] municipality-specific enrichment adapters
- [ ] nationwide vector/static delivery strategy
- [ ] national performance tests
- [ ] source update monitoring
- [ ] automatic data vintage/change notices

## Non-goals for the first MVP

- full nationwide 3D city model
- real-time ingestion of every municipal dataset
- replacing ArcGIS/QGIS analysis workflows
- hiding data uncertainty or source differences behind a single unexplained number
