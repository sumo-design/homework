import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

def draw_annual_trend(works_df, save_path):
    """Draw a professional dual-axis chart for yearly publication and citation counts."""
    if works_df.empty:
        return
        
    # Group by year
    df_valid = works_df.dropna(subset=['year']).copy()
    df_valid['year'] = df_valid['year'].astype(int)
    
    # Exclude 2026 as it's an incomplete year in our data, to prevent misleading downward slopes
    df_valid = df_valid[df_valid['year'] < 2026]
    
    yearly = df_valid.groupby('year').agg(
        pubs=('work_id', 'count'),
        citations=('cited_by_count', 'sum')
    ).reset_index()
    
    yearly = yearly.sort_values('year')
    
    fig, ax1 = plt.subplots(figsize=(10, 5.5), dpi=300)
    plt.title("Annual Publication and Citation Trends in Photonic Computing", fontsize=14, fontweight='bold', pad=15)
    
    # Colors matching premium styling
    pub_color = '#4A6FA5'
    cit_color = '#D66853'
    
    # Left axis - Publications Bar Chart
    ax1.bar(yearly['year'], yearly['pubs'], color=pub_color, alpha=0.8, width=0.6, label='Publications')
    ax1.set_xlabel('Year', fontsize=12, labelpad=10)
    ax1.set_ylabel('Annual Publications (Count)', color=pub_color, fontsize=12)
    ax1.tick_params(axis='y', labelcolor=pub_color)
    ax1.set_xticks(yearly['year'])
    ax1.set_xticklabels(yearly['year'], rotation=45)
    ax1.grid(True, axis='y', linestyle='--', alpha=0.3)
    
    # Right axis - Citations Line Chart
    ax2 = ax1.twinx()
    ax2.plot(yearly['year'], yearly['citations'], color=cit_color, linewidth=2.5, marker='o', label='Citations')
    ax2.set_ylabel('Annual Citations (Count)', color=cit_color, fontsize=12)
    ax2.tick_params(axis='y', labelcolor=cit_color)
    
    fig.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved annual trend plot: {save_path}")

def draw_network(G, save_path, title="Network Map", top_labels=5, seed=42):
    """Draw a static PNG network map with community coloring and degree-based sizing.
    Strictly aligned with Degree Centrality for node sizes, Louvain partition for VOSviewer-like coloring,
    and limited to Top 5 labeled nodes with layout spacing optimized to prevent overlaps.
    """
    if len(G) == 0:
        return
        
    plt.figure(figsize=(11, 10), dpi=300)
    plt.title(title, fontsize=14, fontweight='bold', pad=10)
    
    # Try Kamada-Kawai layout; fallback to spring layout with huge k=3.0 if graph is disconnected
    try:
        pos = nx.kamada_kawai_layout(G)
    except Exception:
        pos = nx.spring_layout(G, k=3.0/np.sqrt(len(G)), iterations=200, seed=seed)
    
    # Compute degrees for node sizing (Degree Centrality based sizing)
    deg = dict(G.degree())
    max_deg = max(deg.values()) if deg else 1
    
    # High-contrast sizing: core nodes are significantly larger
    node_sizes = [30 + 1000 * (deg[n] / max_deg) ** 1.8 for n in G.nodes()]
    
    # Try Louvain community detection for coloring using built-in networkx
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
        
    # VOSviewer native high-saturation colors
    vos_colors = [
        '#ff4444', # Cluster 0: Red
        '#33b5e5', # Cluster 1: Blue
        '#00C851', # Cluster 2: Green
        '#ffbb33', # Cluster 3: Orange
        '#aa66cc', # Cluster 4: Purple
        '#E91E63', # Cluster 5: Pink (additional)
        '#0097A7', # Cluster 6: Teal (additional)
        '#455A64', # Cluster 7: Grey (additional)
        '#E64A19', # Cluster 8: Deep Orange (additional)
        '#795548'  # Cluster 9: Brown (additional)
    ]
    node_colors = [vos_colors[partition[n] % len(vos_colors)] for n in G.nodes()]
    
    # Draw edges with weight-based transparency
    weights = [G[u][v].get('weight', 1.0) for u, v in G.edges()]
    max_w = max(weights) if weights else 1.0
    edge_alphas = [0.05 + 0.5 * (w / max_w) for w in weights]
    
    # Draw nodes and edges
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, edgecolors='#4D4D4D', linewidths=0.6, alpha=0.95)
    
    # Draw edges individually to respect alpha mapping
    for (u, v), alpha in zip(G.edges(), edge_alphas):
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], width=0.8, alpha=alpha, edge_color='#B3B3B3')
        
    # Annotate Top 5 nodes based on degree centrality to prevent overlap
    top_nodes = sorted(deg.items(), key=lambda x: x[1], reverse=True)[:5]
    labels = {node: node for node, _ in top_nodes}
    
    # Shift labels significantly above the node center (+0.06) to prevent label overlapping on node circles
    label_pos = {node: (coords[0], coords[1] + 0.06) for node, coords in pos.items()}
    
    # Draw labels with very small font size (7)
    nx.draw_networkx_labels(
        G, label_pos, labels=labels, 
        font_size=7, font_weight='bold', font_family='sans-serif',
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.8, lw=0.5)
    )
    
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved static network PNG: {save_path}")

def draw_network_interactive(G, save_path, title="Interactive Network Map", metrics_df=None, seed=42):
    """Generate an interactive HTML visualization using vis.js via a standalone script template.
    Synced with the exact same community coloring, degree centrality sizing, and top-5 labeling logic.
    """
    if len(G) == 0:
        return
        
    # Get layout position (consistent spacing layout)
    try:
        pos = nx.kamada_kawai_layout(G)
    except Exception:
        pos = nx.spring_layout(G, k=3.0/np.sqrt(len(G)), iterations=200, seed=seed)
    
    # Create community partition using built-in networkx
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
        
    # Map metrics for tooltips
    metrics_map = {}
    if metrics_df is not None and not metrics_df.empty:
        for _, r in metrics_df.iterrows():
            metrics_map[r['node']] = {
                'degree': int(r['degree']),
                'w_degree': float(r['weighted_degree']),
                'betweenness': float(r['betweenness']),
                'pagerank': float(r['pagerank']),
                'closeness': float(r['closeness'])
            }
            
    # VOSviewer native high-saturation colors
    vos_colors = [
        '#ff4444', # Cluster 0: Red
        '#33b5e5', # Cluster 1: Blue
        '#00C851', # Cluster 2: Green
        '#ffbb33', # Cluster 3: Orange
        '#aa66cc', # Cluster 4: Purple
        '#E91E63', # Cluster 5: Pink (additional)
        '#0097A7', # Cluster 6: Teal (additional)
        '#455A64', # Cluster 7: Grey (additional)
        '#E64A19', # Cluster 8: Deep Orange (additional)
        '#795548'  # Cluster 9: Brown (additional)
    ]
    
    deg = dict(G.degree())
    max_deg = max(deg.values()) if deg else 1
    
    # Identify Top 5 nodes to display labels on to remain consistent with static graph
    top_nodes_set = set(node for node, _ in sorted(deg.items(), key=lambda x: x[1], reverse=True)[:5])
    
    nodes_js = []
    for node in G.nodes():
        cid = partition.get(node, 0)
        color = vos_colors[cid % len(vos_colors)]
        deg_val = deg[node]
        
        # Build tooltip as plain text
        m = metrics_map.get(node, {})
        tooltip = (
            f"Node: {node}\n"
            f"Degree: {deg_val}\n"
            f"Cluster: {cid}\n"
        )
        if m:
            tooltip += (
                f"Weighted Degree: {m['w_degree']:.2f}\n"
                f"Betweenness Centrality: {m['betweenness']:.4f}\n"
                f"PageRank: {m['pagerank']:.4f}\n"
                f"Closeness: {m['closeness']:.4f}"
            )
            
        # Synced High-Contrast Sizing for HTML (scaled appropriately for vis.js nodes, typically size 8 to 68)
        size = 8 + 60 * (deg_val / max_deg) ** 1.8
        
        # Display label only for top 5 nodes, other nodes have label empty but show details on hover
        display_label = node if node in top_nodes_set else ""
        
        nodes_js.append({
            'id': node,
            'label': display_label,
            'x': float(pos[node][0]) * 1000,
            'y': float(pos[node][1]) * 1000,
            'color': color,
            'size': int(size),
            'title': tooltip,
            'font': {'size': 12, 'face': 'arial', 'strokeWidth': 3, 'strokeColor': '#ffffff', 'bold': True}
        })
        
    edges_js = []
    for u, v, data in G.edges(data=True):
        w = data.get('weight', 1.0)
        edges_js.append({
            'from': u,
            'to': v,
            'value': float(w),
            'title': f"Co-occurrence weight: {w}",
            'color': {'color': '#CCCCCC', 'highlight': '#888888'}
        })
        
    # vis.js HTML Template
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style type="text/css">
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 0; background-color: #f8f9fa; }}
    .header {{ background: linear-gradient(135deg, #4A6FA5 0%, #354E71 100%); color: white; padding: 15px 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
    .header h2 {{ margin: 0; font-size: 20px; }}
    #network-container {{ width: 100%; height: calc(100vh - 60px); background-color: #ffffff; }}
  </style>
</head>
<body>
  <div class="header">
    <h2>{title} (Interactive Map)</h2>
  </div>
  <div id="network-container"></div>
  <script type="text/javascript">
    var container = document.getElementById('network-container');
    var data = {{
      nodes: new vis.DataSet({json.dumps(nodes_js)}),
      edges: new vis.DataSet({json.dumps(edges_js)})
    }};
    var options = {{
      nodes: {{
        shape: 'dot',
        scaling: {{ min: 8, max: 68 }}
      }},
      edges: {{
        scaling: {{ min: 1, max: 10 }},
        smooth: {{ type: 'continuous' }}
      }},
      physics: {{
        enabled: false
      }},
      interaction: {{
        hover: true,
        tooltipDelay: 200,
        zoomView: true,
        dragView: true
      }}
    }};
    var network = new vis.Network(container, data, options);
  </script>
</body>
</html>
"""
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Saved interactive network HTML: {save_path}")
