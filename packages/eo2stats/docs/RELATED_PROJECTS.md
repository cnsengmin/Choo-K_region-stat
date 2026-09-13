# Related Open-Source Projects

Last reviewed: 2026-09-13

`eo2stats` should reuse mature projects and focus on the missing semantic/research layer.

## 1. QGIS MCP

Example:
- https://github.com/jjsantos01/qgis_mcp

What it already does:
- connects an AI client to QGIS via MCP
- creates/loads QGIS projects
- adds/removes vector and raster layers
- executes QGIS Processing algorithms
- renders maps
- can run PyQGIS code

Relationship to eo2stats:

```text
QGIS MCP = control QGIS
EO2Stats  = understand/retrieve/transform EO and urban indicators reproducibly
```

Do not duplicate QGIS project-control features unless a dedicated adapter is needed.

## 2. GeoAI

Repository:
- https://github.com/opengeos/geoai

Useful capabilities:
- satellite/aerial imagery discovery and preprocessing
- training-chip generation
- segmentation
- classification
- object detection
- change detection
- raster↔vector conversion
- building/water/land-cover extraction
- foundation-model catalog/integration

Relationship:
- use as a candidate feature-extraction adapter
- retain model/version/confidence provenance
- convert extracted geometry into urban-form indicators in eo2stats

## 3. segment-geospatial / SamGeo

Repository:
- https://github.com/opengeos/segment-geospatial

Useful capabilities:
- Segment Anything models for geospatial imagery
- text/point/polygon prompting
- time-series segmentation
- vector export
- QGIS plugin

Relationship:
- candidate interactive or automated imagery→object adapter
- eo2stats should not reimplement SAM infrastructure

## 4. Microsoft Global ML Building Footprints

Repository:
- https://github.com/microsoft/GlobalMLBuildingFootprints

Why it matters:
- demonstrates imagery → semantic segmentation → polygonization at global scale
- releases building footprint polygons and, in some regions, height estimates
- includes confidence/vintage considerations

Relationship:
- source/validation dataset where coverage and licensing permit
- reference architecture for large-scale building extraction
- useful benchmark against local cadastral/building data

## 5. PySAL / tobler

Repository:
- https://github.com/pysal/tobler

Capabilities:
- area-weighted interpolation
- dasymetric mapping
- model-based interpolation
- change of spatial support
- small-area estimation tools

Relationship:
- preferred engine for explicitly permitted administrative-data spatialization
- eo2stats adds the policy layer deciding whether an indicator should be interpolated at all

## 6. WorldPop methodology

WorldPop demonstrates model-based dasymetric disaggregation of administrative population totals using high-resolution covariates such as:
- buildings/settlement
- roads
- land cover
- night lights
- terrain and other geospatial variables

Relationship:
- methodological reference for `disaggregatable_extensive` indicators
- not a justification for disaggregating arbitrary social ratios

## 7. pystac-client

Repository:
- https://github.com/stac-utils/pystac-client

Role:
- common Python search client for STAC APIs

Relationship:
- default dataset/scene discovery layer

## 8. odc-stac / stackstac

Repositories:
- https://github.com/opendatacube/odc-stac
- https://github.com/gjoseph92/stackstac

Role:
- load STAC raster assets into xarray/Dask-compatible time-space structures

Relationship:
- benchmark both for scene/time-series loading before choosing defaults

## 9. STAC Browser

Repository:
- https://github.com/radiantearth/stac-browser

Role:
- browse STAC catalogs, collections, items and assets visually

Relationship:
- candidate base for future dataset-discovery UI

## 10. OSMnx

Repository:
- https://github.com/gboeing/osmnx

Role:
- street-network acquisition/modeling and urban network measures

Relationship:
- candidate topology engine after roads are sourced from OSM or extracted/normalized from other data

## 11. The gap eo2stats should target

Existing projects already solve much of:

```text
image search
image loading
segmentation
vectorization
GIS operations
network analysis
MCP control of QGIS
```

The missing integrated layer is closer to:

```text
What does this dataset actually measure?
↓
At what spatial/temporal support?
↓
Can it validly be transformed to my research unit?
↓
If physical imagery, what urban objects/form can be derived?
↓
If administrative statistics, is redistribution valid or only contextual?
↓
What method and assumptions were used?
↓
Can the result be reproduced and audited?
```

That semantic + provenance + urban-research layer is the intended contribution of `eo2stats`.