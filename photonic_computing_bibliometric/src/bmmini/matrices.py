"""
matrices.py - 显式矩阵构建
对标指南 Step 5：从数据表构建核心矩阵

公式参考：
- 共被引矩阵：C = A.T @ A，其中 A 为 paper-reference 二部矩阵
- 文献耦合矩阵：B = A @ A.T
- 关键词共现矩阵：W = K.T @ K
- 合作网络矩阵：N = M.T @ M
"""

import scipy.sparse as sp
import numpy as np
import pandas as pd


def build_incidence_matrix(df, row_col, col_col, data_col=None):
    """
    构建二部矩阵 A
    
    用途：作为投影前的原始矩阵，后续可通过 A.T @ A 或 A @ A.T 生成投影矩阵
    
    Parameters
    ----------
    df : pd.DataFrame
        长表，包含 (row_col, col_col[, data_col])
    row_col : str
        行索引列名，如 'work_id'
    col_col : str
        列索引列名，如 'reference_id'
    data_col : str, optional
        数据值列名，默认为 1（即一条一条边）
    
    Returns
    -------
    A : scipy.sparse._matrix (CSR format)
        稀疏矩阵
    rows : list
        行标签列表
    cols : list
        列标签列表
    
    Example
    -------
    >>> ref_df = pd.DataFrame({
    ...     'work_id': ['P1', 'P1', 'P2'],
    ...     'reference_id': ['R1', 'R2', 'R2']
    ... })
    >>> A, papers, refs = build_incidence_matrix(ref_df, 'work_id', 'reference_id')
    >>> print(A.shape)  # (3, 2) - 3 papers, 2 refs
    (3, 2)
    """
    df = df.dropna(subset=[row_col, col_col])
    
    rows_unique = sorted(df[row_col].unique())
    cols_unique = sorted(df[col_col].unique())
    
    row_idx = {v: i for i, v in enumerate(rows_unique)}
    col_idx = {v: i for i, v in enumerate(cols_unique)}
    
    row_indices = np.array([row_idx[v] for v in df[row_col]])
    col_indices = np.array([col_idx[v] for v in df[col_col]])
    
    if data_col and data_col in df.columns:
        data = df[data_col].values.astype(float)
    else:
        data = np.ones(len(df))
    
    A = sp.coo_matrix(
        (data, (row_indices, col_indices)),
        shape=(len(rows_unique), len(cols_unique))
    ).tocsr()
    
    return A, rows_unique, cols_unique


def co_citation_edges(ref_df, min_weight=1):
    """
    共被引网络：C = A.T @ A
    
    定义：两篇参考文献被同一批论文共同引用的次数
    
    Parameters
    ----------
    ref_df : pd.DataFrame
        work_references.csv，字段：work_id, reference_id
    min_weight : int
        边权重最小值，默认 1
    
    Returns
    -------
    edges_df : pd.DataFrame
        字段：source, target, weight
        其中 source/target 是 reference_id
    
    Formula
    -------
    A: paper-reference 矩阵，A[i,j] = 1 if paper i cites ref j
    C = A.T @ A
    C[i,j] = 论文 i 和论文 j 被同一批论文共同引用的次数
    
    Reference
    ---------
    Lesson 7: Co-citation analysis
    """
    A, papers, refs = build_incidence_matrix(ref_df, "work_id", "reference_id")
    
    # 计算 C = A.T @ A
    C = A.T @ A
    C.setdiag(0)  # 去掉自环
    C = C.tocoo()
    
    edges = []
    for i, j, w in zip(C.row, C.col, C.data):
        if i < j:  # 去掉对称重复
            weight = int(w)
            if weight >= min_weight:
                edges.append({
                    "source": refs[i],
                    "target": refs[j],
                    "weight": weight
                })
    
    return pd.DataFrame(edges)


def bibliographic_coupling_edges(ref_df, min_weight=1):
    """
    文献耦合网络：B = A @ A.T
    
    定义：两篇论文共享参考文献的次数（表示研究方向接近度）
    
    Parameters
    ----------
    ref_df : pd.DataFrame
        work_references.csv
    min_weight : int
        边权重最小值
    
    Returns
    -------
    edges_df : pd.DataFrame
        source/target 是 work_id
    
    Formula
    -------
    B = A @ A.T
    B[i,j] = 论文 i 和论文 j 共享的参考文献数量
    
    Reference
    ---------
    Lesson 8: Bibliographic coupling & collaboration networks
    """
    A, papers, refs = build_incidence_matrix(ref_df, "work_id", "reference_id")
    
    B = A @ A.T
    B.setdiag(0)
    B = B.tocoo()
    
    edges = []
    for i, j, w in zip(B.row, B.col, B.data):
        if i < j:
            weight = int(w)
            if weight >= min_weight:
                edges.append({
                    "source": papers[i],
                    "target": papers[j],
                    "weight": weight
                })
    
    return pd.DataFrame(edges)


def keyword_cooccurrence_edges(kw_df, min_weight=1):
    """
    关键词共现网络：W = K.T @ K
    
    定义：两个关键词在同一篇论文中共现的次数
    
    Parameters
    ----------
    kw_df : pd.DataFrame
        work_keywords.csv，字段：work_id, keyword
    min_weight : int
        边权重最小值
    
    Returns
    -------
    edges_df : pd.DataFrame
    
    Formula
    -------
    K: paper-keyword 矩阵
    W = K.T @ K
    W[i,j] = keyword i 和 keyword j 共现的次数
    """
    K, papers, keywords = build_incidence_matrix(kw_df, "work_id", "keyword")
    
    W = K.T @ K
    W.setdiag(0)
    W = W.tocoo()
    
    edges = []
    for i, j, w in zip(W.row, W.col, W.data):
        if i < j:
            weight = int(w)
            if weight >= min_weight:
                edges.append({
                    "source": keywords[i],
                    "target": keywords[j],
                    "weight": weight
                })
    
    return pd.DataFrame(edges)


def coauthorship_edges(auth_df, min_weight=1):
    """
    合作网络：N = M.T @ M
    
    Parameters
    ----------
    auth_df : pd.DataFrame
        work_authors.csv，字段：work_id, author_id (or author_name)
    min_weight : int
    
    Returns
    -------
    edges_df : pd.DataFrame
        source/target 是 author_id/author_name
    
    Formula
    -------
    M: paper-author 矩阵
    N = M.T @ M
    N[i,j] = author i 和 author j 共同发表论文数
    """
    if 'author_id' in auth_df.columns:
        author_col = 'author_id'
    elif 'author_name' in auth_df.columns:
        author_col = 'author_name'
    else:
        raise ValueError("需要 'author_id' 或 'author_name' 列")
    
    M, papers, authors = build_incidence_matrix(auth_df, "work_id", author_col)
    
    N = M.T @ M
    N.setdiag(0)
    N = N.tocoo()
    
    edges = []
    for i, j, w in zip(N.row, N.col, N.data):
        if i < j:
            weight = int(w)
            if weight >= min_weight:
                edges.append({
                    "source": authors[i],
                    "target": authors[j],
                    "weight": weight
                })
    
    return pd.DataFrame(edges)
