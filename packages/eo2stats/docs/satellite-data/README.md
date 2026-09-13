# Satellite & EO Data Catalog

이 폴더는 `eo2stats`에서 사용하는 위성·원격탐사·지형 자료의 **연구용 데이터 사전**이다.

목적은 매 분석마다 다음 내용을 다시 조사하는 비용을 줄이는 것이다.

- 공간적 coverage와 타일/scene 구조
- 사용 가능한 시간 범위와 재방문 특성
- sensor / product / processing level
- band·변수의 의미
- 저장값(DN)과 물리량의 관계
- unit, scale factor, offset, nodata
- QA/cloud mask
- 시계열 비교 시 주의점
- STAC/provider 접근 경로
- DEM·건물·도로·인구·기상 등 외부자료와의 결합 방식

## Initial catalog

| Dataset | Type | Primary research role |
|---|---|---|
| `sentinel-2-l2a.md` | optical | fine-scale vegetation/water/built-up change |
| `landsat-c2-l2.md` | optical + thermal | long time series and surface temperature |
| `sentinel-1-grd.md` | SAR | cloud-resistant backscatter and structural context |
| `copernicus-dem.md` | DEM | elevation/slope/aspect and SAR terrain processing |
| `hls-v2.md` | harmonized optical | Landsat + Sentinel 30 m time series |

## Machine-readable header

각 MD는 사람이 읽는 설명과 함께 YAML front matter를 가진다.

```yaml
dataset_id: sentinel-2-l2a
mission: Copernicus Sentinel-2
sensor: MSI
product: Level-2A
processing_level: L2A
data_category: optical
spatial_resolution: 10m/20m/60m
temporal_role: dynamic
physical_unit: reflectance_unitless
preferred_access: STAC+COG
last_verified: 2026-09-13
```

향후 이 header를 읽어 catalog UI, MCP resource, provider config를 자동 생성할 수 있게 한다.

## Rule

**센서 이름만으로 처리식을 결정하지 않는다.**

같은 mission이라도 product level, processing baseline, provider, asset metadata에 따라 값의 의미가 달라질 수 있다. Unit/scale/offset/QA는 공식 product guide 또는 asset metadata로 검증한다.
