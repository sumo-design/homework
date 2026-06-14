"""
qc.py - 网络质量检查与敏感性分析
对标指南 Step 9：质量检查与敏感性分析
"""

import pandas as pd
import numpy as np
import networkx as nx


def network_qc(edges_df, network_name="unnamed"):
    """
    计算网络级质量指标
    
    Parameters
    ----------
    edges_df : pd.DataFrame
        source, target, weight
    network_name : str
        网络名称
    
    Returns
    -------
    qc_row : dict
        包含 n_nodes, n_edges, density, n_components, largest_component_ratio
    
    Reference
    ---------
    Lesson 5: Network indicators
    """
    if edges_df is None or edges_df.empty:
        return {
            "network": network_name,
            "n_nodes": 0,
            "n_edges": 0,
            "density": np.nan,
            "n_components": 0,
            "largest_component_ratio": np.nan,
            "avg_weight": np.nan
        }
    
    # 构建网络
    G = nx.from_pandas_edgelist(
        edges_df,
        "source", "target",
        edge_attr="weight",
        create_using=nx.Graph()
    )
    
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    
    if n_nodes <= 1:
        density = 0.0
        n_components = 1 if n_nodes == 1 else 0
        largest_component_ratio = 1.0 if n_nodes == 1 else 0.0
    else:
        density = nx.density(G)
        n_components = nx.number_connected_components(G)
        
        if n_components > 0:
            lcc = max(nx.connected_components(G), key=len)
            largest_component_ratio = len(lcc) / n_nodes
        else:
            largest_component_ratio = 0.0
    
    avg_weight = edges_df["weight"].mean() if len(edges_df) > 0 else 0.0
    
    return {
        "network": network_name,
        "n_nodes": n_nodes,
        "n_edges": n_edges,
        "density": round(density, 4),
        "n_components": n_components,
        "largest_component_ratio": round(largest_component_ratio, 4),
        "avg_weight": round(avg_weight, 2)
    }


def generate_qc_report(edges_dict):
    """
    生成统一的质量检查报告
    
    Parameters
    ----------
    edges_dict : dict
        {network_name: edges_df, ...}
    
    Returns
    -------
    qc_df : pd.DataFrame
    
    Example
    -------
    >>> edges_dict = {
    ...     'co_citation': co_edges,
    ...     'bibliographic_coupling': bc_edges,
    ...     'keyword_cooccurrence': kw_edges
    ... }
    >>> qc_df = generate_qc_report(edges_dict)
    >>> qc_df.to_csv('outputs/tables/network_qc_summary.csv', index=False)
    """
    qc_results = []
    for net_name, edges_df in edges_dict.items():
        qc = network_qc(edges_df, net_name)
        qc_results.append(qc)
    
    return pd.DataFrame(qc_results)


def sensitivity_analysis(ref_df, kw_df, auth_df=None,
                        min_weights=[1, 2, 3],
                        top_edges_list=None):
    """
    阈值敏感性分析
    
    测试不同 min_edge_weight 或 top_edges 参数下的网络质量变化
    
    Parameters
    ----------
    ref_df : pd.DataFrame
        work_references.csv
    kw_df : pd.DataFrame
        work_keywords.csv
    auth_df : pd.DataFrame, optional
        work_authors.csv
    min_weights : list
        要测试的最小权重列表
    top_edges_list : list, optional
        要测试的 top_edges 数量
    
    Returns
    -------
    sensitivity_df : pd.DataFrame
    
    Example
    -------
    >>> sens_df = sensitivity_analysis(ref_df, kw_df, min_weights=[1, 2, 3])
    >>> sens_df.to_csv('outputs/tables/sensitivity_summary.csv', index=False)
    """
    from .matrices import (
        co_citation_edges,
        bibliographic_coupling_edges,
        keyword_cooccurrence_edges,
        coauthorship_edges
    )
    
    results = []
    
    # 测试 min_edge_weight
    for min_w in min_weights:
        for network_type, edges_func, data in [
            ("co_citation", co_citation_edges, ref_df),
            ("bibliographic_coupling", bibliographic_coupling_edges, ref_df),
            ("keyword_cooccurrence", keyword_cooccurrence_edges, kw_df),
        ]:
            try:
                edges = edges_func(data, min_weight=min_w)
                qc = network_qc(edges, f"{network_type}_min_w={min_w}")
                qc["param"] = f"min_weight={min_w}"
                results.append(qc)
            except Exception as e:
                print(f"⚠️ Error in {network_type} with min_w={min_w}: {e}")
    
    # 作者合作网络（如果数据可用）
    if auth_df is not None and not auth_df.empty:
        for min_w in min_weights:
            try:
                edges = coauthorship_edges(auth_df, min_weight=min_w)
                qc = network_qc(edges, f"coauthorship_min_w={min_w}")
                qc["param"] = f"min_weight={min_w}"
                results.append(qc)
            except Exception as e:
                print(f"⚠️ Error in coauthorship with min_w={min_w}: {e}")
    
    return pd.DataFrame(results)
