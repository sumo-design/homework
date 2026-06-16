# 光子计算文献计量分析（2015–2026）

本项目为湖南大学《文献计量学和前沿趋势追踪》课程的期末大作业成果仓库。项目针对光子计算（Photonic Computing）领域 2015–2026 年间的学术文献进行全流程挖掘、矩阵投射网络分析与科学知识图谱可视化。项目包含 VOSviewer 基础分析 与 Python 进阶文献计量流水线 的双轨交叉验证，是一套完整、规范且 100% 可复现的学术计量项目。

---

## 一、 小组成员与分工 (Team & Division of Labor)

本项目由课程小组合作完成，具体分工与实验报告首页一致：
* 辛成诚 (学号：202314010225): 负责检索式构建、原始数据下载与检索、VOSviewer 基础计量网络（合作、共现、共被引）分析，以及 IMRaD 学术论文 (`实验报告.docx`) 核心内容撰写。
* 刘博林 (学号：202314010218): 负责 Python 进阶文献计量流水线开发、稀疏矩阵投射算法设计与单元测试编写、项目文档整理、图谱极致视觉优化，以及论文和 PPT 格式规范控制。

---

## 二、 数据说明 (Dataset & Metrics)

本研究严格遵循课程要求的方法透明度标准，数据口径说明如下：
* 数据来源： Clarivate Analytics Web of Science (WoS) 核心合集（Core Collection）
* 检索式： `TS=("photonic computing" OR "optical computing" OR "photonic neural network" OR "optical neural network" OR "photonic reservoir computing")`
* 检索日期： 2026 年 6 月 14 日（精确到日）
* 文献时间范围： 2015 年 1 月 1 日 – 2026 年 6 月 14 日
* 文献类型： 仅纳入 Article、Review、Proceedings Paper
* 有效文献数量： 5,000 篇（经 UT 唯一标识符精确去重）
* 核心计量指标：
  * 文献总数： 5,000 篇
  * 总被引频次： 116,088 次
  * 篇均被引数： 23.22 次
  * H 指数： 137
  * 唯一作者数： 8,298 人
* 数据清洗规则： 基于 WoS 唯一标识符（UT 字段）进行精准去重；作者姓名统一归一化为 `[姓氏, 首字母.]`（如 `Shen Y.`）格式以消除重名与拼写变体歧义；发文机构进行清洗和合并归一化。

---

## 三、 运行步骤说明 (How to Run)

本项目代码在 Python 3.11 环境下测试运行正常。为了能顺利跑通，请按照以下步骤操作（如果您平时习惯用虚拟环境，可以建一个 venv，不建的话直接在全局环境跑也完全可以）：

### 3.1 安装依赖包
在终端（CMD 或 PowerShell）中进入项目根目录，运行以下命令安装所需的第三方库：
```bash
pip install -r requirements.txt
```
### 3.2 一键运行主流水线
直接运行根目录下的 `run.py`，即可一键解析原始文献数据、自动计算各项网络计量指标并生成全部的图表、表格与交互式 HTML 网页：
```bash
python run.py
```
(提示：主脚本内部已自动处理了 `src` 的路径加载，不需要在终端手动配置复杂的 `PYTHONPATH` 环境变量，直接运行命令即可。)

### 3.3 运行单元测试（可选）
如果需要验证网络矩阵投影的数学计算公式是否正确，可以直接运行 pytest 测试脚本：
```bash
python -m pytest tests/test_matrices.py -v
```
(提示：同样不需要设置环境变量，直接在根目录下运行即可，测试结果应为 100% 通过。)


---

## 四、 项目目录结构 (Repository Structure)

项目目录树严格遵循课程推荐规范：
```
photonic_computing_bibliometric/
├── run.py                          # 项目主运行入口，一键执行完整分析流水线
├── requirements.txt                # 锁定版本号的包依赖声明文件
├── config/                         # 项目配置目录
│   └── query.yaml                 # 检索配置、数据路径及分析阈值配置文件
├── data/                           # 数据集目录
│   ├── raw/                        # WoS 导出的 Tagged-Text 格式原始数据包
│   └── processed/                  # 清洗归一化后的四张标准关系长表 csv
│       ├── works_clean.csv         # 种子文献主表（5,000条有效文献）
│       ├── work_references.csv     # 文献引用关联长表
│       ├── work_keywords.csv       # 文献关键词关联长表
│       └── work_authors.csv        # 文献作者-机构关联长表
├── src/                            # 核心源代码目录
│   └── bmmini/                     # 文献计量分析核心包
│       ├── __init__.py             # 包初始化
│       ├── utils.py                # 配置加载与清洗消歧函数
│       ├── parse_wos.py            # WOS 原始文本解析与长表结构化
│       ├── matrices.py             # 科学网络二部矩阵投影模块 (C=A.T@A, B=A@A.T)
│       ├── metrics.py              # 网络级 QC 拓扑指标与节点中心性计算
│       ├── visualize.py            # Matplotlib 趋势图与 vis.js 交互式图谱生成
│       └── pipeline.py             # 串联全流程的分析流水线
├── tests/                          # 自动化测试目录
│   └── test_matrices.py            # 验证矩阵投影与数学转换正确性的测试脚本
├── outputs/                        # 流水线运行产出物（和你本地文件完全一致）
│   ├── tables/                     # 生成的所有数据指标表
│   │   ├── network_qc_summary.csv              # 四类网络质量控制拓扑指标对比汇总表
│   │   ├── network_metrics_co_citation.csv     # 共被引网络节点级中心性指标表
│   │   ├── network_metrics_coauthorship.csv    # 作者合作网络节点级中心性指标表
│   │   ├── network_metrics_keyword_cooccurrence.csv # 关键词共现网络节点级中心性指标表
│   │   ├── network_metrics_bibliographic_coupling.csv # 文献耦合网络节点级中心性指标表
│   │   ├── descriptive_indicators.csv          # 种子文献整体描述性统计指标表
│   │   ├── cluster_summary_co_citation.csv     # 共被引网络Louvain聚类汇总表
│   │   ├── cluster_summary_coauthorship.csv    # 作者合作网络Louvain聚类汇总表
│   │   ├── cluster_summary_keyword_cooccurrence.csv # 关键词共现网络Louvain聚类汇总表
│   │   ├── cluster_summary_bibliographic_coupling.csv # 文献耦合网络Louvain聚类汇总表
│   │   ├── co_citation_edges.csv               # 共被引网络边列表
│   │   ├── coauthorship_edges.csv              # 作者合作网络边列表
│   │   ├── keyword_cooccurrence_edges.csv      # 关键词共现网络边列表
│   │   ├── bibliographic_coupling_edges.csv    # 文献耦合网络边列表
│   │   └── top_authors.csv                     # 核心作者发文量与被引排名表
│   ├── figures/                    # 所有静态PNG图（和你本地文件完全一致）
│   │   ├── annual_trend.png                  # 发文与被引年度趋势图（回答RQ1）
│   │   ├── coauthorship_network.png          # 作者合作网络图
│   │   ├── keyword_cooccurrence_network.png  # 关键词共现网络图
│   │   ├── co_citation_network.png           # 文献共被引网络图
│   │   ├── bibliographic_coupling_network.png # 文献耦合网络图
│   │   └── vosviewer_*.png                   # VOSviewer导出的所有原始图谱（聚类/密度/Overlay视图）
│   └── html/                       # 交互式网页网络图
│       ├── coauthorship_network.html         # 作者合作交互式图谱
│       ├── keyword_cooccurrence_network.html # 关键词共现交互式图谱
│       ├── co_citation_network.html          # 共被引交互式图谱
│       └── bibliographic_coupling_network.html # 文献耦合交互式图谱
├── reports/                        # 自动生成的分析报告
│   └── bibliometrics_report.html   # 响应式综合数据报告（集成所有核心图表）
├── docs/                           # 学术规范与参数说明
│   ├── ai_usage.md                # AI 工具使用与核验说明（学术诚实性）
│   └── params.md                  # 阈值参数（min_edge_weight、top_edges等）选择理据
├── paper/                          # 课程正式论文
│   └── 实验报告.docx               # 标准 IMRaD 结构的课程论文终稿 Word 版
├── presentation/                   # 答辩汇报材料
│   └── final_presentation.pptx     # 严格符合 8 页结构的答辩 PPT
└── reflection/                     # 个人学习反思
    └── reflection.docx             # 组员学习总结与分工自评表
```

---

## 五、 输出成果说明 (Outputs & Deliverables)

1. 静态学术图表 (outputs/figures/)
   ·annual_trend.png：光子计算 2015-2025 年度发文量与引文增长趋势图，直观呈现领域爆发式增长轨迹，对应研究问题 RQ1
   ·4 类核心网络图谱：coauthorship_network.png（作者合作）、keyword_cooccurrence_network.png（关键词共现）、co_citation_network.png（文献共被引）、bibliographic_coupling_network.png（文献耦合），所有图均已优化：节点大小对应度中心性、颜色对应 Louvain 聚类、仅标注 Top5 核心节点解决标签重叠问题
   ·VOSviewer 原始图谱：包含关键词、合作、共被引三类网络的聚类视图、密度视图、时间演化视图，作为 Python 分析的交叉验证基准
2. 全量指标数据 (outputs/tables/)
   ·网络质量控制表：network_qc_summary.csv，记录四类网络的节点数、边数、密度、连通分支数、模块度等核心拓扑指标，用于科学图谱的质量校验
   ·节点中心性表：4 类网络的network_metrics_*.csv，包含每个节点的度数、加权度、中介中心性、PageRank 等完整指标，是论文所有结论的核心数据支撑
   ·聚类与边表：cluster_summary_*.csv（Louvain 社区划分结果）、各类网络的边列表文件，可直接导入其他工具二次分析
   ·基础统计表：descriptive_indicators.csv（文献整体统计）、top_authors.csv（核心作者排名），用于领域基础特征描述
3. 交互式网页图谱 (outputs/html/)
   ·4 类网络均生成了独立的交互式 HTML 图谱：支持鼠标缩放、拖拽节点，鼠标悬浮可查看节点完整信息（名称、度、中心性、社区 ID），彻底解决静态图标签重叠的问题，适合答辩展示。
4. 课程交付文档
   · paper/实验报告.docx：严格符合 IMRaD 结构的课程终稿论文，包含 10 项方法透明度、3 图 1 表、完整交叉验证说明
   ·presentation/final_presentation.pptx：严格遵循课件要求的 8 页结构答辩 PPT
   ·reflection/reflection.docx：小组学习反思与分工自评报告
   ·docs/目录：包含 AI 使用说明、参数选择理据、数据质量报告等全部学术合规文档

---

## 六、 项目验收标准 (Acceptance Criteria)

本项目完全对标课程要求，达成以下验收标准：
1. VOSviewer 网络完整性： 严格按照课程要求，利用 VOSviewer GUI 完成了关键词共现网络、机构合作网络、文献共被引网络 3 类科学网络构建，导出了对应的网络视图、密度视图和 Overlay 时间演化视图，并作为数据基准存放于仓库。
2. Python 自建流水线可复现性： 支持 `python run.py` 一键无报错运行。自动执行 WOS 原始文本的清洗去重、四类关系长表构建、矩阵二部投影（共被引 C=A^T·A、耦合 B=A·A^T、共现 W=K^T·K、合作 N=M^T·M）、网络拓扑指标计算及图表自动输出。
3. 单元测试覆盖率： 单元测试 (`tests/test_matrices.py`) 覆盖了稀疏矩阵投影和 Betweenness 中心性距离转换等核心算法逻辑，测试通过率 100%。
4. 论文符合 IMRaD 规范： 论文主体架构完整，Methods 部分满足最低 10 项透明度要素，正文引用与 References 列表完全对应，Claim 与 Evidence (3图1表) 严格绑定，无无据预测。

---

## 七、 参考文献与致谢 (References & Acknowledgements)

### 7.1 核心参考文献
1. Shen Y, Harris N C, Skirlo S, et al. Deep learning with coherent nanophotonic circuits[J]. Nature Photonics, 2017, 11(7): 441-446.
2. Xu X, Tan M, Corcoran B, et al. 11 TOPS photonic convolutional accelerator for optical neural networks[J]. Nature, 2021, 589(7840): 44-51.
3. Feldmann J, Youngblood N, Wright C D, et al. Parallel convolutional processing using an integrated photonic tensor core[J]. Nature, 2021, 589(7840): 52-58.
4. Brunner D, Soriano M C, Mirasso C R, et al. Parallel photonic information processing at gigabyte per second data rates using transient states[J]. Nature Communications, 2013, 4(1): 1-8.
5. Miller D A B. Optical interconnects to electronic chips[J]. Applied Optics, 2010, 49(25): F59-F70.

### 7.2 致谢
衷心感谢课程任课老师杨其晟副教授在文献计量学原理与学术规范上的悉心指导。感谢小组成员的紧密协作。同时，感谢智能开发工具在本项目代码开发、消歧匹配算法优化及文档格式整理过程中的高效辅助。
