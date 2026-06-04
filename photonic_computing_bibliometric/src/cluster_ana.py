import networkx as nx,community,pandas as pd
def louvain_cluster(mat,thres):
    G=nx.Graph()
    for i in range(len(mat)):
        for j in range(i+1,len(mat)):
            w=mat.iloc[i,j]
            if w>=thres:
                G.add_edge(mat.index[i],mat.columns[j],weight=w)
    part=community.best_partition(G,weight="weight")
    info=[]
    for c in set(part.values()):
        nodes=[k for k,v in part.items() if v==c]
        sub=G.subgraph(nodes)
        info.append({"聚类编号":c,"关键词数量":len(nodes),"网络密度":round(nx.density(sub),3),"核心关键词":max(nodes,key=lambda x:sub.degree(x))})
    return G,part,pd.DataFrame(info)
