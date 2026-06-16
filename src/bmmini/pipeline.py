import os
from pathlib import Path
from datetime import datetime
import pandas as pd

from .utils import load_config, ensure_dirs
from .parse_wos import parse_wos_dir, save_normalized_wos
from .matrices import (
    co_citation_edges,
    bibliographic_coupling_edges,
    keyword_cooccurrence_edges,
    coauthorship_edges
)
from .metrics import (
    graph_from_edges,
    node_metrics,
    network_summary,
    cluster_summary,
    descriptive_indicators
)
from .visualize import (
    draw_annual_trend,
    draw_network,
    draw_network_interactive
)

def run_pipeline(config_path="config/query.yaml"):
    """Run the complete bibliometrics analysis pipeline."""
    print("=" * 60)
    print("[RUNNING] PHOTONIC COMPUTING BIBLIOMETRICS PIPELINE")
    print("=" * 60)
    
    config = load_config(config_path)
    ensure_dirs(config)
    
    raw_dir = Path(config['data']['raw_dir'])
    processed_dir = Path(config['data']['processed_dir'])
    
    # 1. Parse and Clean Raw Data
    print("\n[Step 1] Loading and parsing raw WOS data...")
    records = parse_wos_dir(raw_dir)
    print(f"Total raw WOS records parsed: {len(records)}")
    
    print("\n[Step 2] Normalizing and saving clean tables...")
    paths = save_normalized_wos(records, processed_dir)
    
    # Read processed tables
    works = pd.read_csv(paths['works'])
    refs = pd.read_csv(paths['references'])
    authors = pd.read_csv(paths['authors'])
    keywords = pd.read_csv(paths['keywords'])
    
    min_w = config['analysis'].get('min_edge_weight', 2)
    top_edges = config['analysis'].get('top_edges', 200)
    seed = config['analysis'].get('layout_seed', 42)
    top_labels = config['analysis'].get('top_labels', 15)
    
    # 2. Build Networks
    print("\n[Step 3] Constructing sparse network matrices and projecting edges...")
    edge_tables = {
        'keyword_cooccurrence': keyword_cooccurrence_edges(keywords, min_weight=min_w, top_edges=top_edges),
        'co_citation': co_citation_edges(refs, min_weight=min_w, top_edges=top_edges),
        'bibliographic_coupling': bibliographic_coupling_edges(refs, min_weight=min_w, top_edges=top_edges),
        'coauthorship': coauthorship_edges(authors, min_weight=min_w, top_edges=top_edges)
    }
    
    summaries = []
    network_results = {}
    
    # Process each network
    for name, edges in edge_tables.items():
        print(f"  - Modeling network: {name} ({len(edges)} edges projected)")
        # Save edges CSV
        edges.to_csv(f"outputs/tables/{name}_edges.csv", index=False, encoding='utf-8-sig')
        
        # Build networkx graph
        G = graph_from_edges(edges)
        
        # Calculate node-level metrics
        metrics = node_metrics(G)
        metrics.to_csv(f"outputs/tables/network_metrics_{name}.csv", index=False, encoding='utf-8-sig')
        
        # Save cluster summary
        csum = cluster_summary(metrics)
        if not csum.empty:
            csum.to_csv(f"outputs/tables/cluster_summary_{name}.csv", index=False, encoding='utf-8-sig')
            
        # Compute network-level summary
        summary = network_summary(G)
        summary['network'] = name
        summaries.append(summary)
        
        # Draw Visualizations
        title_display = name.replace('_', ' ').title()
        draw_network(G, f"outputs/figures/{name}_network.png", title=f"Photonic Computing: {title_display}", top_labels=top_labels, seed=seed)
        draw_network_interactive(G, f"outputs/html/{name}_network.html", title=f"Photonic Computing: {title_display}", metrics_df=metrics, seed=seed)
        
        network_results[name] = {
            'graph': G,
            'edges': edges,
            'metrics': metrics,
            'cluster_summary': csum,
            'summary': summary
        }
        
    # Save quality control summary
    qc_df = pd.DataFrame(summaries)
    qc_df.to_csv("outputs/tables/network_qc_summary.csv", index=False, encoding='utf-8-sig')
    
    # Save descriptive indicators
    desc_ind = descriptive_indicators(works, authors)
    desc_ind.to_csv("outputs/tables/descriptive_indicators.csv", index=False, encoding='utf-8-sig')
    
    # Save annual publication trends
    draw_annual_trend(works, "outputs/figures/annual_trend.png")
    
    # 3. Generate HTML report
    print("\n[Step 4] Compiling comprehensive HTML report...")
    _generate_html_report(
        network_results=network_results,
        desc_indicators=desc_ind,
        n_works=len(works),
        n_refs=len(refs),
        n_authors=len(authors),
        n_keywords=len(keywords),
        min_w=min_w,
        top_edges=top_edges,
        seed=seed
    )
    
    print("\n" + "=" * 60)
    print("[SUCCESS] PIPELINE SUCCESSFULLY COMPLETED!")
    print("=" * 60)

def _df_to_html_table(df, max_rows=15):
    """Convert pandas DataFrame to styled HTML table."""
    if df is None or df.empty:
        return "<p class='text-muted'>No data available.</p>"
    disp = df.head(max_rows).copy()
    disp = disp.map(lambda x: f"{x:.4f}" if isinstance(x, float) else x)
    return disp.to_html(classes="table table-striped table-hover table-sm table-bordered", index=False, escape=False)

def _generate_html_report(network_results, desc_indicators, n_works, n_refs, n_authors, n_keywords, min_w, top_edges, seed):
    """Generate a responsive HTML report embedding all figures and statistics."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    desc_row = desc_indicators.iloc[0] if not desc_indicators.empty else {}
    
    # Format network sections
    sections = []
    net_titles = {
        'keyword_cooccurrence': 'Keyword Co-occurrence Network (W = K.T @ K)',
        'co_citation': 'Co-citation Network (C = A.T @ A)',
        'bibliographic_coupling': 'Bibliographic Coupling Network (B = A @ A.T)',
        'coauthorship': 'Co-authorship Collaboration Network (N = M.T @ M)'
    }
    
    for name in ['keyword_cooccurrence', 'co_citation', 'bibliographic_coupling', 'coauthorship']:
        if name not in network_results:
            continue
        res = network_results[name]
        s = res['summary']
        metrics = res['metrics']
        csum = res['cluster_summary']
        title = net_titles[name]
        
        overview = [
            ('Nodes', s['n_nodes']),
            ('Edges', s['n_edges']),
            ('Density', f"{s['density']:.4f}"),
            ('Communities', s['n_communities']),
            ('Modularity', f"{s['modularity']:.4f}"),
            ('Avg Clustering', f"{s['avg_clustering_coefficient']:.4f}"),
            ('Avg Degree', f"{s['avg_degree']:.2f}"),
            ('Avg Weighted Degree', f"{s['avg_weighted_degree']:.2f}"),
            ('Components Count', s['n_components']),
            ('Largest Component %', f"{s['largest_component_ratio']:.2%}")
        ]
        
        overview_html = "".join([f"<tr><th>{lbl}</th><td>{val}</td></tr>" for lbl, val in overview])
        
        sec = f"""
        <div id="section-{name}" class="network-section card mb-5 shadow-sm">
            <div class="card-header bg-dark text-white">
                <h3 class="card-title my-1" style="font-size:1.3rem;">{title}</h3>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-5">
                        <h5>Network Quality Metrics</h5>
                        <table class="table table-sm table-bordered">
                            <tbody>
                                {overview_html}
                            </tbody>
                        </table>
                    </div>
                    <div class="col-md-7 text-center">
                        <h5>Static Topology Visualisation</h5>
                        <img src="../outputs/figures/{name}_network.png" class="img-fluid rounded border shadow-sm" alt="{title}" style="max-height: 380px;"/>
                    </div>
                </div>
                
                <hr class="my-4"/>
                
                <div class="row">
                    <div class="col-12">
                        <h5>Interactive Vis.js Web Map</h5>
                        <iframe src="../outputs/html/{name}_network.html" width="100%" height="450" frameborder="0" class="border rounded shadow-sm"></iframe>
                    </div>
                </div>
                
                <div class="row mt-4">
                    <div class="col-md-6">
                        <h5>Top-10 Node Centralities</h5>
                        {_df_to_html_table(metrics, 10)}
                    </div>
                    <div class="col-md-6">
                        <h5>Louvain Community Profiles</h5>
                        {_df_to_html_table(csum, 8)}
                    </div>
                </div>
            </div>
        </div>
        """
        sections.append(sec)
        
    sections_html = "\n".join(sections)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Photonic Computing Bibliometric Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{ background-color: #f5f6f8; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        .jumbotron {{ background: linear-gradient(135deg, #2A4365 0%, #1A202C 100%); color: white; padding: 40px 20px; margin-bottom: 30px; border-radius: 0 0 10px 10px; }}
        .network-section {{ background-color: white; border: none; border-radius: 8px; overflow: hidden; }}
        .table th {{ background-color: #f7fafc; width: 45%; }}
        .toc-list .list-group-item-action {{ cursor: pointer; }}
    </style>
</head>
<body>
    <div class="jumbotron shadow">
        <div class="container">
            <h1 class="display-6 fw-bold">Photonic Computing (光子计算) Bibliometric Report</h1>
            <p class="lead opacity-75">Knowledge Structure and Topological Network Analysis (2015-2026)</p>
            <p class="small opacity-50 mb-0">Compiled on {now} | Data scope: 5,010 WoS publications</p>
        </div>
    </div>
    
    <div class="container">
        <div class="row">
            <div class="col-lg-3 mb-4">
                <div class="card shadow-sm sticky-top" style="top: 20px;">
                    <div class="card-header bg-primary text-white fw-bold">Table of Contents</div>
                    <div class="list-group list-group-flush toc-list">
                        <a href="#overview" class="list-group-item list-group-item-action">Descriptive Overview</a>
                        <a href="#section-keyword_cooccurrence" class="list-group-item list-group-item-action">Keyword Co-occurrence</a>
                        <a href="#section-co_citation" class="list-group-item list-group-item-action">Reference Co-citation</a>
                        <a href="#section-bibliographic_coupling" class="list-group-item list-group-item-action">Bibliographic Coupling</a>
                        <a href="#section-coauthorship" class="list-group-item list-group-item-action">Author Collaboration</a>
                    </div>
                </div>
            </div>
            
            <div class="col-lg-9">
                <section id="overview" class="card mb-5 shadow-sm">
                    <div class="card-header bg-secondary text-white">
                        <h4 class="mb-0" style="font-size:1.15rem;">Descriptive Overview & Indicators</h4>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-5">
                                <table class="table table-bordered table-sm">
                                    <tbody>
                                        <tr><th>Total Seed Papers</th><td>{n_works:,}</td></tr>
                                        <tr><th>H-index (Seed Works)</th><td>{int(desc_row.get('h_index_seed_works', 0))}</td></tr>
                                        <tr><th>Total Citations</th><td>{int(desc_row.get('total_citations', 0)):,}</td></tr>
                                        <tr><th>Mean Citations / Work</th><td>{desc_row.get('mean_citations', 0.0)}</td></tr>
                                        <tr><th>Unique Authors</th><td>{int(desc_row.get('n_authors', 0)):,}</td></tr>
                                        <tr><th>Reference Relations</th><td>{n_refs:,}</td></tr>
                                        <tr><th>Unique Keywords</th><td>{n_keywords:,}</td></tr>
                                    </tbody>
                                </table>
                                <p class="small text-muted"><b>Pipeline Parameters:</b> min_edge_weight={min_w}, top_edges={top_edges}, seed={seed}</p>
                            </div>
                            <div class="col-md-7 text-center">
                                <h5>Annual Publication Trend</h5>
                                <img src="../outputs/figures/annual_trend.png" class="img-fluid rounded border shadow-sm" alt="Annual Trend" style="max-height: 280px;"/>
                            </div>
                        </div>
                    </div>
                </</section>
                
                {sections_html}
            </div>
        </div>
    </div>
    
    <footer class="bg-dark text-white text-center py-3 mt-5">
        <small>Photonic Computing Bibliometrics pipeline | Associate Professor Qisheng Yang spring 2026 course project</small>
    </footer>
</body>
</html>
"""
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    with open(reports_dir / "bibliometrics_report.html", "w", encoding="utf-8") as f:
        f.write(html)
