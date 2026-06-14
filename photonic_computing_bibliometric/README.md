# 光子计算文献计量学分析项目

一个完整的文献计量学分析框架，用于分析光子计算领域的学术论文数据。

## 📊 项目功能

- **数据加载与清洗**：支持 WOS 格式数据
- **指标计算**：基本计量指标统计
- **共现分析**：关键词共现矩阵构建
- **聚类分析**：Louvain 算法识别研究热点
- **可视化**：
  - 年度论文发表趋势图
  - 交互式知识图谱（HTML）
- **报告生成**：自动生成 Markdown 分析报告

## 🚀 快速开始

### 1. 环境设置

```bash
# 安装依赖
pip install -r requirements.txt

# 或者使用 conda
conda create -n photonic-bib python=3.9
conda activate photonic-bib
pip install -r requirements.txt
```

### 2. 准备数据

将 WOS 导出的数据文件放在 `data/` 目录：
```
data/
├── sample-wos/          # WOS 格式数据文件（必需）
└── processed/           # 处理后的数据（自动生成）
```

### 3. 运行分析

#### 简单运行（推荐）
```bash
python run.py
```

#### 完整管道运行
```bash
python run_pipeline.py
```

## 📁 项目结构

```
photonic_computing_bibliometric/
├── README.md                    # 项目文档
├── requirements.txt             # Python 依赖
├── config.py                    # 配置文件
├── run.py                       # 主运行脚本
├── run_pipeline.py              # 完整管道脚本
├── check_cited.py               # 被引用文献检查脚本
│
├── src/                         # 核心模块
│   ├── __init__.py
│   ├── bib_read.py             # 数据加载
│   ├── data_clean.py           # 数据清洗
│   ├── index_calc.py           # 指标计算
│   ├── co_occur.py             # 共现分析
│   ├── cluster_ana.py          # 聚类分析
│   ├── static_draw.py          # 静态图表
│   ├── inter_draw.py           # 交互式图表
│   └── report_build.py         # 报告生成
│
├── data/                        # 数据目录
│   ├── sample-wos/             # 输入：WOS 数据
│   └── processed/              # 自动生成：处理后数据
│
├── outputs/                     # 输出目录
│   ├── figures/                # 生成的图表
│   ├── tables/                 # 生成的表格
│   └── html/                   # 交互式网络图
│
├── reports/                     # 报告目录
│   └── bibliometric_report.md  # 自动生成的分析报告
│
├── config/                      # 配置文件目录
└── docs/                        # 文档目录
```

## ⚙️ 配置说明

编辑 `config.py` 调整参数：

```python
DATA_PATH = "data/sample-wos"      # WOS 数据路径
TOP_KEY = 50                       # 提取最频繁的关键词数
EDGE_THRESH = 2                    # 共现网络边权重阈值
TABLE_OUT = "outputs/tables"       # 表格输出目录
FIG_OUT = "outputs/figures"        # 图表输出目录
HTML_OUT = "outputs/html"          # 网络图输出目录
```

## 📊 输出文件

### 图表
- `发表趋势.png` - 按年份统计的论文发表数
- `共现网络.html` - 交互式知识图谱

### 表格
- `基本统计.csv` - 基本计量指标
- `聚类结果.csv` - 研究热点聚类结果
- `共现矩阵.csv` - 关键词共现矩阵

### 报告
- `bibliometric_report.md` - 完整分析报告（Markdown 格式）

## 🔧 核心模块说明

| 模块 | 功能 |
|------|------|
| `bib_read.py` | 读取 WOS 格式数据 |
| `data_clean.py` | 数据清洗和预处理 |
| `index_calc.py` | 计算文献计量指标（发表量、被引次数等） |
| `co_occur.py` | 构建关键词共现矩阵 |
| `cluster_ana.py` | 使用 Louvain 算法进行社团检测 |
| `static_draw.py` | 生成静态图表 |
| `inter_draw.py` | 生成交互式网络可视化 |
| `report_build.py` | 生成 Markdown 格式的分析报告 |

## 📋 依赖包

- `pandas` - 数据处理
- `numpy` - 数值计算
- `networkx` - 网络分析
- `scikit-learn` - 机器学习/聚类
- `matplotlib` - 绘图
- `pyyaml` - YAML 配置
- `openpyxl` - Excel 支持

## 🐛 故障排除

### 数据加载失败
- 确保 WOS 文件在 `data/sample-wos/` 目录
- 检查文件格式是否正确

### 模块导入错误
- 确保在项目根目录运行脚本
- 检查 Python 环境是否正确安装依赖

### 内存不足
- 在 `config.py` 中减少 `TOP_KEY` 值
- 使用更小的数据集进行测试

## 📝 许可证

MIT License

## 👤 作者

xcc-alpha

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
