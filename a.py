from statistics import correlation

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from numpy.ma.extras import unique
from wordcloud import WordCloud
import sqlite3

from query_test import df_netflix

#veriyi çek
conn = sqlite3.connect('netflix.db')
df_netflix = pd.read_sql_query("SELECT * FROM netflix WHERE listed_in IS NOT NULL;",conn)
conn.close()

#eksik director hucrelerini "unknown ile doldur
df_netflix["director"] = df_netflix["director"].fillna("Unknown")
df_netflix["cast"]= df_netflix["cast"].fillna("Unknown")
df_netflix["country"] = df_netflix["country"].fillna("Unknown")
df_netflix["date_added"] = df_netflix["date_added"].fillna("Unknown")
df_netflix["rating"] = df_netflix["rating"].fillna(0)
df_netflix["duration"] = df_netflix["duration"].fillna(0)