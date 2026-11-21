# Land-Use Classification Defaults

Use these defaults when no project-specific planning codebook is supplied.

## Group Order And Colors

| Group | Color | Typical raw classes and keywords |
| --- | --- | --- |
| 灞呬綇鐢ㄥ湴 | `#F2C36B` | residential, housing, 灞呬綇, 浣忓畢, 灞呮皯 |
| 宸ヤ笟涓庣敓浜х敤鍦?| `#A98274` | industrial, works, warehouse, logistics, 宸ヤ笟, 浠撳偍, 鐗╂祦, 鐢熶骇 |
| 鍟嗘湇涓庡叕鍏辫鏂界敤鍦?| `#D96C64` | commercial, retail, institutional, office, school, hospital, 鍟嗕笟, 鍟嗘湇, 鍏叡, 鏁欒偛, 鍖荤枟, 鏂囧寲, 浣撹偛 |
| 缁垮湴涓庡紑鏁炵┖闂?| `#6FA869` | park, grass, green, forest, garden, village_green, 鍏洯, 缁垮湴, 鏋楀湴, 鑽夊湴, 寮€鏁?|
| 姘翠綋涓庢父鎲╄鏂?| `#6BAED6` | water, water_park, water_hazard, theme_park, 娌? 婀? 姘? 娓告啯 |
| 寰呭紑鍙?寤鸿涓敤鍦?| `#B7B8B2` | brownfield, greenfield, construction, vacant, 妫曞湴, 寰呭紑鍙? 寤鸿涓?|
| 鍐滀笟璁炬柦/鍥壓鐢ㄥ湴 | `#C6CF76` | farmland, orchard, greenhouse_horticulture, agriculture, 鍐滀笟, 鍐滅敯, 鑰曞湴, 鍥壓 |
| 浜ら€氬強闄勫睘璁炬柦 | `#8C9AA8` | garages, parking, transport, road, railway, 鍋滆溅, 浜ら€? 閬撹矾, 閾佽矾 |
| 鍏朵粬 | `#D6D0C2` | unclassified or unmatched values |

## Area Method

Infer a local UTM CRS from the WGS84 centroid. For Hangzhou, centroid-based UTM selection may resolve to EPSG:32650 or EPSG:32651 depending on the exact AOI; record the selected CRS in the manifest.

If the dataset spans several UTM zones or a whole country, switch to a suitable equal-area CRS and record the choice in `artifact_manifest.json`.

## Field Selection

Prefer fields in this order:

1. explicit user-provided `--class-field`;
2. `class`, `landuse`, `subtype`, `fclass`, `type`, `category`;
3. Chinese fields such as `鐢ㄥ湴绫诲瀷`, `鐢ㄥ湴鎬ц川`, `鍦扮被`, `绫诲瀷`, `绫诲埆`;
4. parsed `source_tags`, especially OSM keys `landuse`, `leisure`, `amenity`, `natural`, `building`, `tourism`.

Keep source color fields such as `LandColor`, `color`, `fill`, or `棰滆壊` in tables for audit, but use the grouped cartographic palette for report figures unless the user asks for source colors.

## Raw-to-Report Audit

The renderer keeps the original value from the selected class field in `class_norm` and `class_label`. It assigns `landuse_group` by scanning the raw value against the keyword list above in group order and records the first hit as `mapping_rule`; unmatched values are recorded as `未匹配默认归入：其他`.

For a planning report, treat the group as a descriptive reporting layer, not as an official conversion of statutory land-use codes. Deliver both `landuse_class_summary.csv` and `landuse_class_to_group_mapping.csv`, and use `06_raw_to_report_group_mapping.png` when the report reader needs to audit how the original categories became the chart categories.

## Administrative Study Areas

Use a supplied district/county boundary layer to choose the reporting extent. Pass repeated `--admin-name` options or a comma-separated list, and use `--admin-parent` when names can repeat across cities. The selected boundary is clipped in the land-use source CRS; area is then recalculated after reprojection to the metric `--area-crs`.

