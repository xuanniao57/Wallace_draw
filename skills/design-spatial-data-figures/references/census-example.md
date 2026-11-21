# 示例来源与复现

题目为“增速最快的州是否也是增加人口最多的州”。单位为州，范围为美国 50 州。华盛顿特区和属地不在这个排名内。使用两个年份 4 月 1 日的常住人口计数。增量为两期之差，增长率为增量除以 2010 年常住人口。此处比较普查计数，没有抽样置信区间。

- 数值来自美国人口普查局 Table A 中两列 **Resident Population**。工作簿 SHA-256 为 `b43d76a15547e9ed3b73f309fd2d1f9404d61ab72760b696e4f2868e97252e31`。[原始 XLSX](https://www2.census.gov/programs-surveys/decennial/2020/data/apportionment/apportionment-2020-tableA.xlsx)
- 州界来自本地依赖 `us-atlas@3.0.1` 的预投影 TopoJSON（2017 年 Census 边界、Albers USA 复合投影）。阿拉斯加按该投影缩小并平移，夏威夷平移；本图只比较指标和方位。脚本用唯一州名连接人口表，断言 50 个州全部匹配，SVG 路径保留 FIPS 州码。[US Atlas](https://github.com/topojson/us-atlas) · [D3 Geo](https://d3js.org/d3-geo/path)
- 仓库中的 CSV 可直接重画。若需核查来源，安装 Python 的 openpyxl 后，从本 skill 目录运行 `python scripts/extract_census.py <下载的工作簿> <核查输出.csv>`，将结果与 `assets/resident-population.csv` 对照。
- 用 Node 22 和 npm 从本 skill 目录运行 `npm ci --ignore-scripts`，再运行 `npm run render -- <输出目录>`。安装依赖后，渲染完全在本地完成。输出为分层矢量 SVG，中文字体优先使用微软雅黑或 Noto Sans CJK SC。仓库 examples 提供导出预览。
- 地图展示所有州，分级为负增长及四档非负增速。两个点图独立排序并保留各自单位。两个面板同一州的名称一致，数值在排名确定后保留一位小数。
