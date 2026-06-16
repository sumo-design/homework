import pandas as pd
import numpy as np
import networkx as nx

def graph_from_edges(edges_df):
    """Build a NetworkX undirected graph from an edge list DataFrame."""
    G = nx.Graph()
    if edges_df is None or edges_df.empty:
        return G
    for _, r in edges_df.iterrows():
        G.add_edge(r['source'], r['target'], weight=float(r['weight']))
    return G

def node_metrics(G):
    """Calculate node-level network indicators:
    Degree, Weighted Degree, Betweenness Centrality, PageRank, Closeness, and Community.
    """
    if len(G) == 0:
        return pd.DataFrame(columns=['node', 'degree', 'weighted_degree', 'betweenness', 'pagerank', 'closeness', 'community'])
    
    # 1. Degree & Weighted Degree
    deg = dict(G.degree())
    w_deg = {node: sum(data.get('weight', 1.0) for _, _, data in G.edges(node, data=True)) for node in G.nodes()}
    
    # 2. Betweenness Centrality (similarity weight converted to distance = 1/weight)
    # We create a copy with distance attribute
    G_dist = G.copy()
    for u, v, data in G_dist.edges(data=True):
        w = data.get('weight', 1.0)
        data['distance'] = 1.0 / w if w > 0 else 1e9
    
    betweenness = nx.betweenness_centrality(G_dist, weight='distance')
    
    # 3. PageRank
    pagerank = nx.pagerank(G, weight='weight')
    
    # 4. Closeness Centrality
    closeness = nx.closeness_centrality(G_dist, distance='distance')
    
    # 5. Community Detection
    try:
        comms = nx.community.louvain_communities(G, weight='weight', seed=42)
        partition = {}
        for cid, comm in enumerate(comms):
            for node in comm:
                partition[node] = cid
    except Exception:
        partition = {}
        for cid, comp in enumerate(nx.connected_components(G)):
            for node in comp:
                partition[node] = cid
                
    rows = []
    for node in G.nodes():
        rows.append({
            'node': node,
            'degree': int(deg.get(node, 0)),
            'weighted_degree': float(w_deg.get(node, 0.0)),
            'betweenness': float(betweenness.get(node, 0.0)),
            'pagerank': float(pagerank.get(node, 0.0)),
            'closeness': float(closeness.get(node, 0.0)),
            'community': int(partition.get(node, 0))
        })
        
    df = pd.DataFrame(rows)
    # Sort nodes by degree descending
    df = df.sort_values('degree', ascending=False).reset_index(drop=True)
    return df

def network_summary(G):
    """Calculate network-level quality control indicators (QC summary)."""
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    
    if n_nodes == 0:
        return {
            'n_nodes': 0,
            'n_edges': 0,
            'density': 0.0,
            'n_communities': 0,
            'modularity': 0.0,
            'avg_clustering_coefficient': 0.0,
            'avg_degree': 0.0,
            'avg_weighted_degree': 0.0,
            'n_components': 0,
            'largest_component_ratio': 0.0
        }
        
    density = nx.density(G)
    
    # Community & Modularity
    try:
        comms = nx.community.louvain_communities(G, weight='weight', seed=42)
        n_communities = len(comms)
        comm_sets = comms
        modularity = nx.community.modularity(G, list(comm_sets), weight='weight')
    except Exception:
        n_communities = nx.number_connected_components(G)
        modularity = 0.0
        
    # Clustering coefficient
    avg_clustering = nx.average_clustering(G, weight='weight')
    
    # Degree info
    degrees = [d for _, d in G.degree()]
    avg_deg = sum(degrees) / len(degrees) if degrees else 0.0
    
    w_degrees = [sum(data.get('weight', 1.0) for _, _, data in G.edges(node, data=True)) for node in G.nodes()]
    avg_w_deg = sum(w_degrees) / len(w_degrees) if w_degrees else 0.0
    
    # Connected components
    n_components = nx.number_connected_components(G)
    if n_components > 0:
        lcc = max(nx.connected_components(G), key=len)
        largest_comp_ratio = len(lcc) / n_nodes
    else:
        largest_comp_ratio = 0.0
        
    return {
        'n_nodes': int(n_nodes),
        'n_edges': int(n_edges),
        'density': float(round(density, 4)),
        'n_communities': int(n_communities),
        'modularity': float(round(modularity, 4)),
        'avg_clustering_coefficient': float(round(avg_clustering, 4)),
        'avg_degree': float(round(avg_deg, 2)),
        'avg_weighted_degree': float(round(avg_w_deg, 2)),
        'n_components': int(n_components),
        'largest_component_ratio': float(round(largest_comp_ratio, 4))
    }

def cluster_summary(metrics_df):
    """Summarize Louvain clusters to extract keyword/theme profiles."""
    if metrics_df.empty:
        return pd.DataFrame()
    
    summary = []
    for c, group in metrics_df.groupby('community'):
        size = len(group)
        # Get top 5 representative terms (sorted by degree)
        top_nodes = group.head(5)['node'].tolist()
        summary.append({
            'community': int(c),
            'size': int(size),
            'top_nodes': '; '.join(top_nodes),
            'mean_pagerank': float(group['pagerank'].mean())
        })
    df = pd.DataFrame(summary)
    return df.sort_values('size', ascending=False).reset_index(drop=True)

def h_index(citations):
    """Compute the h-index from a list of citation counts."""
    vals = sorted([int(x) for x in citations if pd.notna(x)], reverse=True)
    h = 0
    for i, c in enumerate(vals, start=1):
        if c >= i:
            h = i
        else:
            break
    return h

def descriptive_indicators(works_df, authors_df):
    """Compute basic bibliometric descriptors of the dataset."""
    if works_df.empty:
        return pd.DataFrame()
    
    n_works = len(works_df)
    year_min = works_df['year'].min()
    year_max = works_df['year'].max()
    total_citations = works_df['cited_by_count'].sum()
    mean_citations = works_df['cited_by_count'].mean()
    n_authors = authors_df['author_name'].nunique() if not authors_df.empty else 0
    
    h_val = h_index(works_df['cited_by_count'])
            
    return pd.DataFrame([{
        'n_works': int(n_works),
        'year_min': int(year_min) if pd.notna(year_min) else None,
        'year_max': int(year_max) if pd.notna(year_max) else None,
        'total_citations': int(total_citations),
        'mean_citations': float(round(mean_citations, 2)),
        'h_index_seed_works': int(h_val),
        'n_authors': int(n_authors)
    }])
