import config
from src.bib_read import load_wos
from src.data_clean import clean_data
from src.index_calc import calc_index
from src.co_occur import build_co
from src.cluster_ana import louvain_cluster
from src.static_draw import draw_year_pic
from src.inter_draw import draw_html_net
from src.report_build import make_md_report

def main():
    df_raw=load_wos(config.DATA_PATH)
    df_cl=clean_data(df_raw)
    base=calc_index(df_cl)
    co_mat,_=build_co(df_cl,config.TOP_KEY)
    G,part,clus_df=louvain_cluster(co_mat,config.EDGE_THRESH)
    draw_year_pic(df_cl)
    draw_html_net(G,part)
    make_md_report(base,clus_df,co_mat)
    print("✅光子计算文献计量全部完成，结果在output")
if __name__=="__main__":
    main()
