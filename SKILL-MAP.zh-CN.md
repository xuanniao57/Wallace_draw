# 科研绘图 skills 对照表

**核查时间：2026-11-21。** 范围包括 Wallace_draw 的四个入口、本机自定义技能权威源与发现镜像、draw.io 和 Figma 插件、项目内的 Hermes 与 Nature 套件，以及此前讨论过的绘图参考。表中“直接”和“转交”按 SKILL.md 的指令及插件注册信息判断。项目内检出、归档副本和外部工具分别标明，避免把磁盘文件数当作已安装技能数。

| Skill 或工具 | 来源及本机状态 | draw.io 关系 | 对流程框架图、深度学习架构图的具体作用 |
|---|---|---|---|
| `compose-hybrid-scientific-figures` | Wallace_draw 定制；权威源与镜像一致 | **条件转交**给实时绘图 skill，也支持 SVG/Figma | **原创科研框架主入口。** 整理研究对象、分支、汇合和证据，确定整图与局部放大的关系。画网络时须另从模型实现取得拓扑。[本库入口](skills/compose-hybrid-scientific-figures/SKILL.md) |
| `recreate-scientific-figure-in-drawio` | 上游插件和定制版的 skill 同名；插件名及定制目录名均为 `drawio-scientific-illustrator` | **直接调用**插件的实时画布、校验及导出工具 | **可编辑制图执行入口。** 逐个添加模块、标签和连接器，检查并保存 .drawio。定制版额外规定参考布局叠图、保留已认可的插图及父子边。[定制版](skills/drawio-scientific-illustrator/SKILL.md) · [上游插件](https://github.com/icebird1998/drawio-scientific-illustrator) |
| `urban-agent-coach` | 本地 agent-harness 的 Pi 共享入口 | **按任务推荐**上述实时绘图 skill | 城市研究任务的总入口。绘图条目同时列出科学工具包、实时 draw.io 和相关参考模块，具体画法由下游决定。 |
| `architecture-diagram` | Hermes 项目内置；本机有项目与原始检出 | 无，生成 HTML 内嵌 SVG | 擅长前后端、服务、数据库、云部署。如果论文解释模型如何部署，这个入口合适；层间张量和残差拓扑需从模型另行整理。[Hermes](https://github.com/NousResearch/hermes-agent) |
| `concept-diagrams` | Hermes 项目内可选 skill | 无，生成 HTML 内嵌 SVG | 适合概念机制、剖面和对象变换，可解释注意力或图上消息传递的直觉。 |
| `excalidraw` | Hermes 项目内置 | 无，输出 Excalidraw JSON | 适合讨论阶段的手绘流程、系统拓扑和分支草稿；结构随模型实现核对。 |
| `figma-generate-diagram` | Codex 的 Figma 插件 | 无，将 Mermaid 转为可编辑 FigJam 图 | 适合协作梳理流程、依赖和时序。可以先核对连接关系，再进行论文排版。 |
| `imagegen` | Codex 系统 skill | 可向组合图提供概念草图 | 在本机流程中用于构思框架、预览构图或制作概念插图；网络连接与维度取自模型实现。 |
| `design-spatial-data-figures` | Wallace_draw 定制 | 无，使用 D3 或现有分析后端 | 负责地图、配对比较、统计分布等**结果面板**；模型性能或空间残差可以从这里进入整张科研图。[本库入口](skills/design-spatial-data-figures/SKILL.md) |
| `urban-landuse-mapping` | Wallace_draw 定制 | 无，用 Python GIS 与 Matplotlib 制图 | 负责用地分类、裁剪、面积及专题地图，可提供研究区与输入图层面板。[本库入口](skills/urban-landuse-mapping/SKILL.md) |
| `nature-figure` | Nature 套件项目内检出；本地版本 `cad6fe4` | 无，主要为 Python/R | 对**整张论文图**最有帮助：确定主图、支持面板、局部放大及最终栏宽。附概念图和统计图范式，可供框架图排版时参照。[本地对应版本](https://github.com/Yuan1z0825/nature-skills/tree/cad6fe4b0332ba5a9039385e88b9a4d7b9a58ef8/skills/nature-figure) |
| `scientific-figure-making` / `figures4papers` | 前者为后者仓库中的 skill；本地 nature-figure 文档记载其整合关系 | 无，主要为 Python/Matplotlib | 提供来自真实论文的概念图、趋势图和对照图脚本。可借鉴画法，模型结构仍取自自己的代码。[原作者仓库](https://github.com/ChenLiu-1996/figures4papers) · [Nature 套件来源说明](https://github.com/Yuan1z0825/nature-skills/blob/cad6fe4b0332ba5a9039385e88b9a4d7b9a58ef8/skills/nature-figure/references/demos.md) |
| `nature-reader` | Nature 套件项目内检出 | 无 | 对照论文原文、图和图注，读清参考架构的模块和作者声称的贡献。 |
| `nature-writing`、`nature-polishing` | 同一 Nature 套件的两个 skill | 无 | 前者建立图与方法、结果段的论证关系，后者润色图注和相关正文。 |
| `nature-data`、`nature-academic-search`、`nature-citation` | 同一 Nature 套件的三个 skill | 无 | 分别处理数据可用性与数据引用、文献检索、文内引用，为图的数据与参考出处提供支持。 |
| `nature-response`、`nature-paper2ppt` | 同一 Nature 套件的两个 skill | 无 | 前者组织对审稿意见的回应，后者从论文选图并组织汇报。以上 Nature 条目共九个不同入口。[九项所在版本](https://github.com/Yuan1z0825/nature-skills/tree/cad6fe4b0332ba5a9039385e88b9a4d7b9a58ef8/skills) |
| `scientific-toolkit-skill`，含 `scientific-visualization`、`matplotlib`、`seaborn`、`networkx` 等模块 | 本机科学工具包；scientific-visualization 标有 K-Dense 作者信息 | 无 | 前三种绘图模块负责统计证据和出版导出。NetworkX 可表示已知的有向拓扑，节点和边需由分析者或模型追踪提供。[出版绘图模块上游](https://github.com/K-Dense-AI/scientific-agent-skills/tree/main/skills/scientific-visualization) |
| `paper-benchmark-analysis`、`paper-knowledge-index` | 本机研究 skill | 无 | 前者拆解已有论文并提取方法和图表，后者索引这些材料，辅助回查参考框架。 |
| `nc-manuscript-craft` | 本机写作 skill | 无 | 对齐论文主张、图注和证据，供整稿编辑使用。 |
| `data-analytics:visualize-data` | Codex Data 插件 | 无 | 在分析报告、仪表板和 notebook 中设计定量图；可为方法图旁边的验证面板提供统计结果。 |
| D3、Observable Plot | 开源可视化库与实例，本库按需使用 | 无 | D3 可给已知层级/图关系布局，Plot 可组织分面和比较图。两者需要输入数据或明确的图结构。[D3](https://d3js.org/) · [Observable Plot](https://observablehq.com/plot/) |
| `drawio-live`、`drawio-file-utils` | draw.io 插件注册的两个 **MCP 服务** | **实际执行** | 前者提供添加形状、连边、截图和保存等操作；后者提供检查、校验和导出等文件操作。两者由同一个绘图 skill 配合使用。 |
| PyTorch FX、Netron | 可选的**模型核对工具**，独立于本库 | 无自动对接 | FX 可从可追踪的 PyTorch 模型取得计算图；Netron 可查看已有 ONNX 等模型的算子与连接。把核实后的模块拓扑交给绘图入口。[PyTorch FX](https://docs.pytorch.org/docs/stable/fx.html) · [Netron](https://github.com/lutzroeder/netron) |

**draw.io 副本核对。** 本机权威源和发现镜像的定制版入口文件一致。插件 1.0.0 自带的入口与已归档的旧顶层入口文件哈希相同。插件提供运行工具，日常定制规则维护在 Wallace_draw；仓库、镜像与归档在清点时各有用途。

## 深度学习架构图怎么画

1. **先画清计算对象。** 从模型定义、实际使用的配置和 `forward` 找到输入、输出、中间特征以及模块间的真实依赖。用代表性输入记录关键形状，必要时用 FX 或导出图交叉核对。动态分支单独查代码，一个输入只覆盖它经过的路径。
2. **把全网络和贡献模块分开。** 主视图按特征分辨率、序列长度或表征类型的变化合并为几个阶段。重复模块用 ×L，区分同构堆叠和共享权重。将论文新增或改动的模块单独展开，让读者能把插图的进出口接回主图。
3. **按网络类型选表示。** 编解码 CNN 把同分辨率层对齐，标清下采样、上采样及跳连的汇合方式；Transformer 展开一个 block，按实现放置注意力、前馈层、归一化与残差；时空图网络区分时间轴、节点轴、特征轴，并画明邻接关系进入哪一步。[U-Net](https://arxiv.org/abs/1505.04597) · [Transformer](https://arxiv.org/abs/1706.03762) · [Graph WaveNet](https://arxiv.org/abs/1906.00121)
4. **在画布上验证可读性和正确性。** 文字、模块、张量边和汇合点分别可编辑。跳连落到实际算子，残差相加检查形状兼容或投影，拼接标明轴。损失与监督支路标“仅训练”并接到对应输出。最终用实现核对一条完整前向路径，再以论文实际栏宽检查标签。

对“从现有深度学习模型到可编辑论文架构图”，本机能组合出 **实现与形状核对 → 组合图 skill 确定抽象层级 → draw.io skill 建图** 的流程。在核查的技能根目录中，未发现把这三步自动串起来的专用入口。
