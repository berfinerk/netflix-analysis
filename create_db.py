import pandas as pd
import sqlite3

df=pd.read_csv("netflix_titles.csv")
conn=sqlite3.connect("netflix.db")
df.to_sql("netflix", conn, if_exists='replace', index=False)

print("Veri başarıyla veritabanına aktarıldı.")