# 光子计算（Photonic Computing）文献计量学分析

## 项目简介

本项目是一个**最小但完整的文献计量学 Python 项目**，用于系统地分析光子计算领域的学术前沿。

### 核心目标
- 自动完成从原始 WOS/OpenAlex 数据到关键词共现、共被引、文献耦合、合作网络的完整流水线
- 透明化矩阵计算过程：所有网络都可追溯到显式的二部矩阵投影
- 提供可复现、可验证、可扩展的最小工程实现

---

## 📐 方法论

### 矩阵定义与网络构建

本项目使用**二部矩阵投影**方法构建文献计量网络。所有网络都可追溯到原始数据表和矩阵运算。

#### 核心矩阵

| 矩阵 | 行/列 | 公式 | 网络名称 | 节点定义 | 边权定义 |
|------|------|------|---------|---------|----------|
| A | paper × reference | - | 基础关联矩阵 | - | - |
| C | reference × reference | **C = A.T @ A** | 共被引网络 | 参考文献 | 被同批论文共同引用次数 |
| B | paper × paper | **B = A @ A.T** | 文献耦合网络 | Seed papers | 共享参考文献数 |
| K | paper × keyword | - | 基础关联矩阵 | - | - |
| W | keyword × keyword | **W = K.T @ K** | 关键词共现网络 | 关键词 | 共现次数 |
| M | paper × author | - | 基础关联矩阵 | - | - |
| N | author × author | **N = M.T @ M** | 合作网络 | 作者 | 共同发表论文数 |

#### 关键计算说明

**1. 共被引矩阵 C = A.T @ A**
```
A[i,j] = 1 表示论文 i 引用了参考文献 j
C[i,j] = 参考文献 i 和 j 被同一批论文共同引用的次数
对角线置 0（去自环）
```

**2. 文献耦合矩阵 B = A @ A.T**
```
B[i,j] = 论文 i 和 j 共享参考文献的数量
对角线置 0
```

**3. 关键词共现矩阵 W = K.T @ K**
```
K[i,j] = 1 表示论文 i 包含关键词 j
W[i,j] = 关键词 i 和 j 在同一篇论文中共现的次数
```

#### 中心性指标

- **Degree**：直接连接的节点数
- **Weighted Degree**：边权总和，反映关联强度
- **Betweenness Centrality**：
  - ⚠️ **重要**：权重表示相似度/强度（越大越近）
  - 需转换为距离：`distance = 1 / weight`
  - 用 `weight="distance"` 计算 betweenness
  - 高 betweenness 节点是不同簇的桥接点
- **PageRank**：考虑邻域重要性的全局影响力指标
- **Community Detection**：使用连通分量或 Louvain 算法

### 质量检查与阈值

每个网络的质量指标存储在 `outputs/tables/network_qc_summary.csv`：

| 指标 | 含义 | 解释 |
|------|------|------|
| n_nodes | 节点数 | 网络规模 |
| n_edges | 边数 | 关联数量 |
| density | 网络密度 | 实际边数 / 可能边数 |
| n_components | 连通分量数 | 图是否碎片化 |
| largest_component_ratio | 最大连通分量占比 | 主结构覆盖程度 |
| avg_weight | 平均权重 | 平均关联强度 |

**阈值参数**（在 `config.py` 中设置）：
- `min_edge_weight`：保留权重 ≥ 该值的边
- `top_edges`：或保留权重最高的前 N 条边
- `top_labels`：在图中标注的节点数量

---

## 🚀 快速开始

### 1. 安装环境

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export PYTHONPATH=src  # Windows PowerShell: $env:PYTHONPATH="src"
```

### 2. 运行完整流程

```bash
# 使用样例数据运行完整项目
python run.py

# 查看质量检查结果
cat outputs/tables/network_qc_summary.csv

# 查看网络指标
cat outputs/tables/network_metrics_co_citation.csv
```

### 3. 运行测试

```bash
# 验证矩阵计算的正确性
pytest tests/test_matrices.py -v

# 运行所有测试
pytest tests/ -v
```

---

## 📁 项目结构

```
photonic_computing_bibliometric/
├── README.md                              # 项目说明
├── requirements.txt                       # Python 依赖
├── config.py                              # 配置参数
├── run.py                                 # 主运行脚本
│
├── src/bmmini/                           # 核心模块
│   ├── __init__.py
│   ├── bib_read.py                       # 数据加载
│   ├── data_clean.py                     # 数据清洗
│   ├── index_calc.py                     # 指标计算
│   ├── co_occur.py                       # 共现分析
│   ├── cluster_ana.py                    # 聚类分析
│   ├── static_draw.py                    # 静态图表
│   ├── inter_draw.py                     # 交互式图表
│   ├── report_build.py                   # 报告生成
│   ├── matrices.py 🆕                    # 显式矩阵构建（Step 5）
│   └── qc.py 🆕                          # 质量检查（Step 9）
│
├── data/                                  # 数据目录
│   ├── raw/                              # 原始数据
│   ├── sample/                           # 样例数据
│   └── processed/                        # 处理后数据
│
├── outputs/                               # 输出目录
│   ├── tables/                           # CSV 表格
│   │   ├── 基本统计.csv
│   │   ├── 聚类结果.csv
│   │   ├── 共现矩阵.csv
│   │   ├── network_qc_summary.csv 🆕    # 网络质量检查
│   │   └── network_metrics_*.csv        # 节点级指标
│   └── figures/                          # PNG 图表
│       ├── 发表趋势.png
│       ├── co_citation_network.png
│       ├── keyword_cooccurrence_network.png
│       └── ...
│
├── reports/                               # 报告目录
│   └── bibliometric_report.md
│
├── tests/ 🆕                              # 单元测试
│   ├── __init__.py
│   └── test_matrices.py                  # 矩阵公式验证
│
and docs/                                 # 文档目录
```

---

## 📊 输出文件与用途

### 表格输出

| 文件 | 内容 | 用途 |
|------|------|------|
| `network_qc_summary.csv` 🆕 | 网络级质量指标 | 评估网络规模、连通性、密度 |
| `network_metrics_*.csv` | 节点级中心性指标 | 识别关键节点、桥接点 |
| `基本统计.csv` | 论文计量指标 | 发表量、被引统计 |
| `聚类结果.csv` | 关键词社团划分 | 研究热点识别 |
| `共现矩阵.csv` | 关键词共现频率 | 主题关联分析 |

### 图表输出

| 图表 | 节点 | 边权 | 用途 |
|------|------|------|------|
| `co_citation_network.png` | 参考文献 | 共被引次数 | 知识基础识别 |
| `keyword_cooccurrence_network.png` | 关键词 | 共现次数 | 研究热点 |
| `bibliographic_coupling_network.png` | 论文 | 共享参考数 | 前沿论文聚集 |
| `coauthorship_network.png` | 作者 | 共同发表数 | 合作群体识别 |
| `发表趋势.png` | - | - | 年度发展趋势 |

---

## 🧪 测试与验证

### 运行单元测试

```bash
# 验证矩阵公式（C=A.T@A, B=A@A.T 等）
pytest tests/test_matrices.py -v

# 输出示例：
# test_co_citation_manual PASSED                                      [ 12%]
# test_bibliographic_coupling_manual PASSED                           [ 25%]
# test_keyword_cooccurrence PASSED                                    [ 37%]
# ...
```

### 验证可复现性

```bash
# 删除输出后重新运行，应生成相同结果
rm -rf outputs/
python run.py
# 对比输出文件 ✓
```

---

## 🔍 常见问题

### Q1: 共被引网络为空
**A:** 检查 `data/processed/work_references.csv` 是否有数据。需要确保原始数据中包含参考文献列表。

### Q2: 图像像毛线团，看不清楚
**A:** 
- 提高 `config.py` 中的 `min_edge_weight` 值
- 或降低 `top_edges` 数量
- 减少 `top_labels` 的标注数量

### Q3: Betweenness 指标很奇怪
**A:** 确认使用了 `distance = 1 / weight` 转换。权重表示相似度，需转换为距离才能正确计算。

### Q4: 作者名称有重复
**A:** 首版使用 author_name；如有 author_id 则优先使用。可通过 `cleaning_rules.yaml` 扩展名称映射。

---

## 📚 方法依据

### 理论基础
- **Lesson 7**：共被引分析 (Co-citation Analysis)
- **Lesson 8**：文献耦合与合作网络 (Bibliographic Coupling & Coauthorship)
- **Lesson 9**：文献计量工具生态 (Bibliometrics Tool Stack)

### 核心参考
- White & McCain (1998)：共被引分析理论
- Newman (2010)：网络科学基础
- NetworkX 官方文档：网络计算
- scipy.sparse 文档：稀疏矩阵优化

### 工具对标
- **bibliometrix / Biblioshiny**：R 语言文献计量标准
- **VOSviewer**：网络可视化工具
- **CiteSpace**：科学计量引文空间分析

---

## 📝 阶段规划

### ✅ 第一阶段（已完成）
- 矩阵层显式实现（matrices.py）
- 质量检查模块（qc.py）
- 单元测试（test_matrices.py）
- 方法论文档完善

### 🔄 第二阶段（课后扩展）
- [ ] config/query.yaml 配置层
- [ ] OpenAlex API 集成
- [ ] GitHub Actions CI/CD

### 🚀 第三阶段（开源二开）
- [ ] 敏感性分析脚本完整化
- [ ] VOSviewer 导出格式支持
- [ ] 自动报告生成
- [ ] Louvain 社团检测

---

## 🎓 使用建议

### 对于学生
1. 先运行 `pytest tests/test_matrices.py` 理解矩阵公式
2. 修改 `config.py` 中的参数，观察输出变化
3. 查看 `outputs/tables/network_qc_summary.csv` 理解阈值影响
4. 阅读源代码中的注释和 docstring

### 对于教师
1. 使用 `--use-sample` 模式作为课堂演示
2. 要求学生改变参数并解释输出变化
3. 检查 pytest 测试覆盖率
4. 要求学生补充方法说明中的局限分析

---

## 📧 联系与反馈

项目基于文献计量学 Python 最小项目指南开发。

**课程链接**：Lesson 15–16 开源项目入门与二开  
**指南版本**：bibliometrics-mini 1.0  
**最后更新**：2026-06-14

---

**🎯 项目验收标准**：
- ✅ 一条命令生成所有图表与表格
- ✅ 矩阵计算公式清晰可追溯
- ✅ 四类网络均有图、表、指标
- ✅ pytest 测试全部通过
- ✅ 每条结论指向具体表或图，附带局限说明
