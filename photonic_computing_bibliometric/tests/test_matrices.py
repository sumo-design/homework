"""
test_matrices.py - 矩阵计算验证
验证 C=A.T@A、B=A@A.T 等公式的正确性
"""

import pytest
import pandas as pd
import numpy as np
from src.bmmini.matrices import (
    build_incidence_matrix,
    co_citation_edges,
    bibliographic_coupling_edges,
    keyword_cooccurrence_edges
)


class TestIncidenceMatrix:
    """测试二部矩阵构建"""
    
    def test_basic_construction(self):
        """验证基本矩阵构建"""
        df = pd.DataFrame({
            "work_id": ["P1", "P1", "P2"],
            "reference_id": ["R1", "R2", "R2"]
        })
        A, papers, refs = build_incidence_matrix(df, "work_id", "reference_id")
        
        assert A.shape == (2, 2)  # 2 papers, 2 refs
        assert set(papers) == {"P1", "P2"}
        assert set(refs) == {"R1", "R2"}
        assert A[0, 0] == 1  # P1 cites R1
        assert A[0, 1] == 1  # P1 cites R2
        assert A[1, 1] == 1  # P2 cites R2
    
    def test_handles_missing_values(self):
        """验证缺失值处理"""
        df = pd.DataFrame({
            "work_id": ["P1", None, "P2"],
            "reference_id": ["R1", "R2", "R2"]
        })
        A, papers, refs = build_incidence_matrix(df, "work_id", "reference_id")
        
        # None 行应被忽略
        assert A.shape == (2, 2)


class TestCoCitation:
    """测试共被引矩阵"""
    
    def test_co_citation_manual(self):
        """手工验证共被引计算"""
        # 构造样例：
        # P1 引用 R1, R2
        # P2 引用 R2, R3
        # P3 引用 R1, R3
        #
        # 共被引矩阵 C = A.T @ A：
        # R1-R2: 被 P1 共引 => weight=1
        # R1-R3: 被 P3 共引 => weight=1
        # R2-R3: 被 P2 共引 => weight=1
        
        ref_df = pd.DataFrame({
            "work_id": ["P1", "P1", "P2", "P2", "P3", "P3"],
            "reference_id": ["R1", "R2", "R2", "R3", "R1", "R3"]
        })
        
        edges = co_citation_edges(ref_df, min_weight=1)
        
        assert len(edges) == 3, f"Expected 3 edges, got {len(edges)}"
        assert all(e["weight"] == 1 for _, e in edges.iterrows())
        
        # 验证边存在
        pairs = set((e["source"], e["target"]) for _, e in edges.iterrows())
        assert len(pairs) == 3
    
    def test_co_citation_removes_self_loops(self):
        """验证自环移除"""
        ref_df = pd.DataFrame({
            "work_id": ["P1", "P1"],
            "reference_id": ["R1", "R1"]
        })
        
        edges = co_citation_edges(ref_df, min_weight=1)
        # 不应该有 R1-R1 的自环
        assert len(edges) == 0
    
    def test_co_citation_min_weight_filtering(self):
        """验证最小权重过滤"""
        ref_df = pd.DataFrame({
            "work_id": ["P1", "P1", "P1", "P2", "P2", "P3"],
            "reference_id": ["R1", "R2", "R3", "R2", "R3", "R1"]
        })
        
        edges1 = co_citation_edges(ref_df, min_weight=1)
        edges2 = co_citation_edges(ref_df, min_weight=2)
        
        assert len(edges2) <= len(edges1)


class TestBibliographicCoupling:
    """测试文献耦合矩阵"""
    
    def test_bibliographic_coupling_manual(self):
        """手工验证文献耦合计算"""
        # B = A @ A.T
        # P1-P3: 共享 R1 => weight=1
        # P1-P2: 共享 R2 => weight=1
        # P2-P3: 共享 R3 => weight=1
        
        ref_df = pd.DataFrame({
            "work_id": ["P1", "P1", "P2", "P2", "P3", "P3"],
            "reference_id": ["R1", "R2", "R2", "R3", "R1", "R3"]
        })
        
        edges = bibliographic_coupling_edges(ref_df, min_weight=1)
        
        assert len(edges) == 3
        assert all(e["weight"] >= 1 for _, e in edges.iterrows())
    
    def test_bibliographic_coupling_removes_self_loops(self):
        """验证自环移除"""
        ref_df = pd.DataFrame({
            "work_id": ["P1", "P1"],
            "reference_id": ["R1", "R2"]
        })
        
        edges = bibliographic_coupling_edges(ref_df, min_weight=1)
        # 不应该有 P1-P1 的自环
        assert all(e["source"] != e["target"] for _, e in edges.iterrows())


class TestKeywordCooccurrence:
    """测试关键词共现矩阵"""
    
    def test_keyword_cooccurrence(self):
        """验证关键词共现"""
        kw_df = pd.DataFrame({
            "work_id": ["P1", "P1", "P2", "P2"],
            "keyword": ["K1", "K2", "K2", "K3"]
        })
        
        edges = keyword_cooccurrence_edges(kw_df, min_weight=1)
        
        # K1-K2: 被 P1 共现 => weight=1
        # K2-K3: 被 P2 共现 => weight=1
        assert len(edges) == 2
        assert all(e["weight"] == 1 for _, e in edges.iterrows())


class TestEdgeFiltering:
    """测试边过滤"""
    
    def test_min_weight_filtering(self):
        """验证最小权重过滤"""
        ref_df = pd.DataFrame({
            "work_id": ["P1", "P1", "P1", "P2", "P2", "P3"],
            "reference_id": ["R1", "R2", "R3", "R2", "R3", "R1"]
        })
        
        # min_weight=1：所有边
        edges1 = co_citation_edges(ref_df, min_weight=1)
        
        # min_weight=2：只保留权重 >= 2 的边
        edges2 = co_citation_edges(ref_df, min_weight=2)
        
        assert len(edges2) <= len(edges1)
        if len(edges2) > 0:
            assert all(e["weight"] >= 2 for _, e in edges2.iterrows())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
