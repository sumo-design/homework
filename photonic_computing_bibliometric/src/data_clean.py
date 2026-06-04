import pandas as pd
def clean_data(df):
    df=df.dropna(subset=["关键词","年份"])
    df=df[df["关键词"].str.strip()!=""]
    df["年份"]=pd.to_numeric(df["年份"],errors="coerce")
    df=df[(df["年份"]>=2020)&(df["年份"]<=2025)]
    return df
