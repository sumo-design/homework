import config
from src.bib_reader import read_wos
from src.data_clean import clean
from src.index_calc import calc_base
from src.co_word import co_matrix
from src.cluster import cluster_ana
from src.plot_static import draw_year
from src.plot_inter import draw_html
from src.report_md import make_report

def main():
    df_raw=read_wos(config.DATA_PATH)
    df_cl=clean(df_raw)
    base=calc_base(df_cl)
    co_mat,_=co_matrix(df_cl,config.TOP_KEY)
    G,part,clus_df=cluster_ana(co_mat,config.EDGE_THRESH)
    draw_year(df_cl)
    draw_html(G,part)
    make_report(base,clus_df,co_mat)
    print("✅分析完毕，结果在outputs")

if __name__=="__main__":
    main()
