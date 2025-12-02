import sqlite3
import pandas as pd
conn =sqlite3.connect("netflix.db")

#tabloları listeleyelim
tables=pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';",conn)
# print(tables)

#toplam içerik sayısı
query = "SELECT COUNT(*) AS total_content FROM netflix;"
df= pd.read_sql_query(query,conn)
# print(df)
# print("*******************************************")


#türlerine göre içerik sayısı
query = """
SELECT type, COUNT(*) AS total
FROM netflix
GROUP BY type;
"""
df=pd.read_sql_query(query,conn)
# print(df)
# print("*******************************************")

#en çok içerik üreten ülkeler
query = """
SELECT country, COUNT(*) AS total
FROM netflix
GROUP BY country
ORDER BY total DESC
LIMIT 10;
"""
df=pd.read_sql_query(query,conn)
# print(df)
# print("*******************************************")

#yıllara göre içerik dağılımı
query = """
SELECT release_year, COUNT(*) AS total
FROM netflix
GROUP BY release_year
ORDER BY release_year;
"""
df=pd.read_sql_query(query,conn)
# print(df)
# print("*******************************************")

#en uzun açıklamaya sahip içerikler
query = """
SELECT title, description, LENGTH(description) AS desc_length
FROM netflix
ORDER BY desc_length DESC
LIMIT 5;
"""
df=pd.read_sql_query(query,conn)
print(df)
# print("*******************************************")

# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_colwidth', None)
# # print(df.head(5))
#
# print("*******************************************")

#hedef kitle analizi(Rating)
# print("\n--- Hedef Kitle (Rating) Dağılımı ---")
query = """
SELECT rating, COUNT(*) AS total
FROM netflix
WHERE rating IS NOT NULL
GROUP BY rating
ORDER BY total DESC
LIMIT 10;
"""
df = pd.read_sql_query(query,conn)
# print(df)
# print("*******************************************")

# print("\n--- Korku (Horror) İçerikleri ---")
#içerisinde horror kelimesi geçen içeriklerin sayısı
query = """
SELECT count(*) as horror_content_count
FROM netflix
WHERE listed_in LIKE '%Horror%';
"""
df=pd.read_sql_query(query,conn)
# print(df)
# print("*******************************************")

#korku filmlerini etiketleme sonrasında özellik diye ekleme
# print("\n--- Dinamik Etiketleme (is_horror) ve Örnek Çıktı ---")
#bu sorgu ile her bir içerik için 'is_horror' sütununda 1 veya 0 etiketi oluşturulur.
query = """
SELECT
    show_id,
    title,
    type,
    listed_in,
    --Etiketleme işlemi: Listed_in' de 'Horror' geçiyorsa 1, geçmiyorsa 0 
    CASE WHEN listed_in LIKE '%Horror%' THEN 1 ELSE 0 END AS is_horror
FROM netflix
--Etiketlediğimiz korku içeriklerini başta görmek için sıralıyoruz
ORDER BY is_horror DESC
LIMIT 10;
"""
df=pd.read_sql_query(query,conn)
# print(df)
# print("*******************************************")

#kalan tek sorgu: tüm gerekli ham veriyi çekme
# print("--- 1. SQL: Tüm Verinin Tek Seferde Çekilmesi ---")
query = """
SELECT
    show_id,
    title,
    "type",
    director,
    "cast",
    country,
    date_added,
    release_year,
    rating,
    duration,
    listed_in,
    description
FROM netflix
WHERE listed_in IS NOT NULL;
"""
df_netflix = pd.read_sql_query(query, conn)
conn.close()













