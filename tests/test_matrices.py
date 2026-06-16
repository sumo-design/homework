import sys
import os

# Get absolute path to the src directory in this project
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
src_path = os.path.join(project_root, "src")
sys.path.append(src_path)

import pandas as pd
from bmmini.matrices import bibliographic_coupling_edges, co_citation_edges
from bmmini.metrics import graph_from_edges, node_metrics, h_index

def test_coupling_and_cocitation_edges():
    refs = pd.DataFrame([
        {'work_id':'P1','reference_id':'R1'},
        {'work_id':'P1','reference_id':'R2'},
        {'work_id':'P2','reference_id':'R1'},
        {'work_id':'P2','reference_id':'R3'},
        {'work_id':'P3','reference_id':'R2'},
        {'work_id':'P3','reference_id':'R3'},
    ])
    coupling = bibliographic_coupling_edges(refs)
    assert len(coupling) == 3
    assert coupling['weight'].sum() == 3
    cocit = co_citation_edges(refs)
    assert len(cocit) == 3
    assert cocit['weight'].sum() == 3

def test_metrics_and_h_index():
    edges = pd.DataFrame([{'source':'A','target':'B','weight':2},{'source':'B','target':'C','weight':1}])
    G = graph_from_edges(edges)
    metrics = node_metrics(G)
    assert 'betweenness' in metrics.columns
    assert h_index([10,8,7,5,4,3,2,1]) == 4
