import scipy.sparse as sp
import numpy as np
import pandas as pd

def build_incidence_matrix(df, row_col, col_col):
    """Build a sparse 0/1 bipartite incidence matrix A from an edge list.
    A[i,j] = 1 represents an association.
    """
    clean = df[[row_col, col_col]].dropna().drop_duplicates()
    row_ids = sorted(clean[row_col].unique())
    col_ids = sorted(clean[col_col].unique())
    
    row_idx = {v: i for i, v in enumerate(row_ids)}
    col_idx = {v: i for i, v in enumerate(col_ids)}
    
    row_indices = np.array([row_idx[v] for v in clean[row_col]])
    col_indices = np.array([col_idx[v] for v in clean[col_col]])
    data = np.ones(len(clean), dtype=np.float32)
    
    A = sp.coo_matrix(
        (data, (row_indices, col_indices)),
        shape=(len(row_ids), len(col_ids))
    ).tocsr()
    
    return A, row_ids, col_ids

def sparse_matrix_to_edges(mat, ids, min_weight=1, top_edges=None):
    """Convert a symmetric square sparse matrix to an undirected edge list.
    Removes self-loops and keeps i < j (upper triangle).
    """
    coo = mat.tocoo()
    rows = []
    for i, j, w in zip(coo.row, coo.col, coo.data):
        if i >= j or w < min_weight:
            continue
        rows.append({
            'source': ids[i],
            'target': ids[j],
            'weight': float(w)
        })
    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=['source', 'target', 'weight'])
    
    df = df.sort_values('weight', ascending=False)
    if top_edges is not None:
        df = df.head(int(top_edges))
    return df.reset_index(drop=True)

def co_citation_edges(ref_df, min_weight=1, top_edges=None):
    """Co-citation network: C = A.T @ A.
    Where A is paper-reference incidence.
    """
    if ref_df.empty:
        return pd.DataFrame(columns=['source', 'target', 'weight'])
    A, papers, refs = build_incidence_matrix(ref_df, 'work_id', 'reference_id')
    C = A.T @ A
    C.setdiag(0)
    C.eliminate_zeros()
    return sparse_matrix_to_edges(C, refs, min_weight=min_weight, top_edges=top_edges)

def bibliographic_coupling_edges(ref_df, min_weight=1, top_edges=None):
    """Bibliographic coupling network: B = A @ A.T.
    Where A is paper-reference incidence.
    """
    if ref_df.empty:
        return pd.DataFrame(columns=['source', 'target', 'weight'])
    A, papers, refs = build_incidence_matrix(ref_df, 'work_id', 'reference_id')
    B = A @ A.T
    B.setdiag(0)
    B.eliminate_zeros()
    return sparse_matrix_to_edges(B, papers, min_weight=min_weight, top_edges=top_edges)

def keyword_cooccurrence_edges(kw_df, min_weight=1, top_edges=None):
    """Keyword co-occurrence network: W = K.T @ K.
    Where K is paper-keyword incidence.
    """
    if kw_df.empty:
        return pd.DataFrame(columns=['source', 'target', 'weight'])
    K, papers, keywords = build_incidence_matrix(kw_df, 'work_id', 'keyword')
    W = K.T @ K
    W.setdiag(0)
    W.eliminate_zeros()
    return sparse_matrix_to_edges(W, keywords, min_weight=min_weight, top_edges=top_edges)

def coauthorship_edges(auth_df, min_weight=1, top_edges=None):
    """Collaboration network: N = M.T @ M.
    Where M is paper-author incidence.
    """
    if auth_df.empty:
        return pd.DataFrame(columns=['source', 'target', 'weight'])
    # Clean author names and ignore empty names
    clean = auth_df.dropna(subset=['work_id', 'author_name']).copy()
    clean['author_name'] = clean['author_name'].str.strip()
    clean = clean[clean['author_name'] != '']
    
    M, papers, authors = build_incidence_matrix(clean, 'work_id', 'author_name')
    N = M.T @ M
    N.setdiag(0)
    N.eliminate_zeros()
    return sparse_matrix_to_edges(N, authors, min_weight=min_weight, top_edges=top_edges)
