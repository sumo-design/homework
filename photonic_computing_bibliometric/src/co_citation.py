import pandas as pd
import re
from scipy.sparse import csr_matrix

def parse_cr_field(cr_text: str) -> list:
    """
    解析CR字段，生成参考文献唯一标识（作者姓氏+年份）
    规则：提取"作者, 年份"组合（忽略期刊名），避免大小写/缩写差异
    """
    if pd.isna(cr_text) or not isinstance(cr_text, str):
        return []
    # 匹配模式：作者姓氏（首字母大写）+ 逗号 + 空格 + 4位年份
    matches = re.findall(r"([A-Z][a-z]+),\s*(\d{4})", cr_text)
    return [f"{author}_{year}" for author, year in matches]

def build_co_citation_edges(df: pd.DataFrame) -> pd.DataFrame:
    """
    生成共被引关系边列表（Source, Target, Weight）
    输入：包含CR字段的DataFrame
    输出：共被引边列表（Source=参考文献A, Target=参考文献B, Weight=共被引次数）
    """
    # 步骤1: 解析每篇文献的参考文献标识
    df["cited_refs"] = df["CR"].apply(parse_cr_field)
    
    # 步骤2: 构建文献-参考文献矩阵（稀疏存储）
    all_refs = set()
    for refs in df["cited_refs"]:
        all_refs.update(refs)
    ref_to_idx = {ref: i for i, ref in enumerate(all_refs)}
    
    rows, cols, data = [], [], []
    for _, row in df.iterrows():
        for ref in row["cited_refs"]:
            rows.append(row.name)  # 文献索引
            cols.append(ref_to_idx[ref])
            data.append(1)
    
    A = csr_matrix(
        (data, (rows, cols)), 
        shape=(len(df), len(all_refs))
    )
    
    # 步骤3: 计算共被引矩阵 C = A^T @ A（仅保留上三角避免重复）
    C = A.T @ A
    coo = C.tocoo()
    
    # 生成边列表（仅保留共被引次数≥2的强关系）
    edges = []
    for i, j, v in zip(coo.row, coo.col, coo.data):
        if i < j and v >= 2:  # **关键过滤：避免噪声**
            edges.append({
                "Source": list(all_refs)[i],
                "Target": list(all_refs)[j],
                "Weight": int(v)
            })
    return pd.DataFrame(edges)
