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
# print(df_netflix.shape)
# print(df_netflix.head(5))
# print(len(df_netflix))

#EDA VE FEATURE
#eksik değerler
# print(df_netflix.isnull().sum())

#eksik director hucrelerini "unknown ile doldur
df_netflix["director"] = df_netflix["director"].fillna("Unknown")
df_netflix["cast"]= df_netflix["cast"].fillna("Unknown")
df_netflix["country"] = df_netflix["country"].fillna("Unknown")
df_netflix["date_added"] = df_netflix["date_added"].fillna("Unknown")
df_netflix["rating"] = df_netflix["rating"].fillna(0)
df_netflix["duration"] = df_netflix["duration"].fillna(0)

#kontol
# print(df_netflix["director"].isna().sum()) #0 olmalı
# print(df_netflix["cast"].isna().sum())
# print(df_netflix["country"].isna().sum())
# print(df_netflix.isnull().sum())

#listed_in_split sütunundaki benzersiz türler
# unique_genres = df_netflix['listed_in'].unique()
# print("Toplam farklı tür sayısı:", len(unique_genres))
# print("Türler:",unique_genres)

#toplam tür sayısı
# Tüm türleri virgülle ayır
df_netflix['listed_in_split'] = df_netflix['listed_in'].str.split(', ')
# Türleri satır satır ayır (explode)
df_genres = df_netflix.explode('listed_in_split')
# Benzersiz türleri bul
unique_genres = df_genres['listed_in_split'].unique()

# print("Toplam Tür Sayısı:", len(unique_genres))
# print("Türler:")
# for g in unique_genres:
#     print("-", g)

#9 kategorilik bir genre_map kategorileri
genre_map = {
    # --- Drama ---
    "TV Dramas": "Drama",
    "Dramas": "Drama",

    # --- Comedy ---
    "TV Comedies": "Comedy",
    "Comedies": "Comedy",
    "Stand-Up Comedy": "Comedy",
    "Stand-Up Comedy & Talk Shows": "Comedy",

    # --- Action & Sci-Fi ---
    "Action & Adventure": "Action",
    "TV Action & Adventure": "Action",
    "Sci-Fi & Fantasy": "Action",

    # --- Thriller / Crime / Mystery / Horror ---
    "Thrillers": "Thriller",
    "Crime TV Shows": "Thriller",
    "TV Mysteries": "Thriller",
    "TV Thrillers": "Thriller",
    "Horror Movies": "Thriller",
    "TV Horror": "Thriller",

    # --- Romance ---
    "Romantic Movies": "Romance",
    "Romantic TV Shows": "Romance",

    # --- Documentary ---
    "Documentaries": "Documentary",
    "Docuseries": "Documentary",
    "Science & Nature TV": "Documentary",

    # --- Kids / Family / Anime ---
    "Children & Family Movies": "Kids",
    "Kids' TV": "Kids",
    "Anime Series": "Kids",
    "Anime Features": "Kids",

    # --- International / Foreign ---
    "International TV Shows": "International",
    "International Movies": "International",
    "British TV Shows": "International",
    "Spanish-Language TV Shows": "International",
    "Korean TV Shows": "International",
    "LGBTQ Movies": "International",
    "Classic & Cult TV": "International",
    "Movies": "International",
    "TV Shows": "International",

    # --- Music / Sports / Faith / Cult ---
    "Music & Musicals": "Other",
    "Sports Movies": "Other",
    "Faith & Spirituality": "Other",
    "Cult Movies": "Other",
    "Classic Movies": "Other",
}
#listed_in sütununu listeye çevir
df_netflix["listed_in"] = df_netflix["listed_in"].str.split(', ')
#genre_group sütunu oluştur, listed_in içindeki her öğeyi map ile 9 kategoriye dönüştür
df_netflix["genre_group"] = df_netflix["listed_in"].apply(
    lambda genres: [genre_map[g] for g in genres if g in genre_map]
)


categories = ["Action", "Comedy", "Drama", "Thriller", "Romance",
              "Documentary", "Kids", "International", "Other"]
#her kategori için 0 ile sütun oluştur
for cat in categories:
    df_netflix[cat]=0
#genre_group bir liste olduğu için her satırda kontrol edip yaz
for index, row in df_netflix.iterrows():
    if isinstance(row['genre_group'], list):
        for genre in row['genre_group']:
            if genre in categories:
                df_netflix.at[index,genre]=1

#kontrol : ilk 5 satır
# print(df_netflix[categories].head())
# print(df_netflix["Drama"].sum())

genre_counts = df_netflix[categories].sum().sort_values(ascending=False)
# print(genre_counts)
#grafik boyutları
plt.figure(figsize = (12,6))
#çubuk grafik
plt.bar(genre_counts.index, genre_counts.values)

#başlık ve etiketler
plt.title("Netflix Tür Frekans Analizi")
plt.xlabel("Türler")
plt.ylabel("Frekans")
plt.xticks(rotation=45, ha='right')

#grafiği götser
# plt.tight_layout()
# plt.show() Netflix’te en popüler tür: Drama
# Belgesel ve Çocuk içerikleri daha az üretilmiş
# Aksiyon ve Komedi orta seviyede


#sütunlar arasındaki kolerasyonu hesaplayarak, iki türün bir içerikte birlikte görülme sıklığını ölçebiliriz.
#kolerasyon matrisi hesaplama
#df_netflix'in sadece kategori sütunlarını kullanarak korelasyonu hesaplarız.Bu matris, türlerin birbiriyle ne kadar sık yan yana geldiğini gösterir.
correlation_matrix = df_netflix[categories].corr()

# print("\n--- Türler Arası Korelasyon Matrisi ---")
# print(correlation_matrix)

# --- Isı Haritası Görselleştirmesi ---

#grafik boyutunu ayarla
plt.figure(figsize = (10,8))

#ısı haritasını oluşturma
sns.heatmap(
    correlation_matrix, #hesaplanan korelasyon matrisi
    annot=True, #korelasyon değerlerini hücrelerin içine yaz
    fmt=".2f",           # Sayıları iki ondalık basamakla göster
    cmap='coolwarm',     # Renk paleti: Mavi (Negatif) ve Kırmızı (Pozitif) ilişkileri ayırır.
    linewidths=.5,       # Hücreler arasına çizgi ekle
    cbar_kws={'label': 'Korelasyon Değeri'} # Renk çubuğu etiketi
)
#başlık ayarla
plt.title("Netflix Türleri Arası Birliktelik (Korelasyon) Isı Haritası")

#eksen ayarları
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
# plt.show()

#kaç film birden fazla türe sahip
df_netflix["genre_count"] = df_netflix[categories].sum(axis=1)
multi_genre_counts = df_netflix["genre_count"].value_counts().sort_index()

plt.figure(figsize = (8,5))
plt.bar(multi_genre_counts.index, multi_genre_counts.values)
plt.xlabel("Bir İçerikte Bulunan Tür Sayısı")
plt.ylabel("İçerik Sayısı")
plt.title("Netflix Çok Türlü İçeriklerin Dağılımı")
plt.xticks(multi_genre_counts.index)
#plt.show()#Tek tür içeren içerikler en yaygın.2 tür barındıran içerikler de oldukça fazla.3+ tür barındıran içerikler daha nadir.

#yıllara göre tür trendleri

df_year_genre = df_netflix.groupby("release_year")[categories].sum()
plt.figure(figsize = (14,6))
plt.plot(df_year_genre.index, df_year_genre["Drama"])
plt.title("YıılaraGöre Drama İçerik Sayıları")
plt.xlabel("Yıl")
plt.ylabel("Drama İçerik Sayısı")
# plt.show()

plt.figure(figsize = (14,7))
for cat in categories:
    plt.plot(df_year_genre.index, df_year_genre[cat],label=cat)

plt.title("Yıllara Göre Netflix Tür Üretim Trendleri")
plt.xlabel("Yıl")
plt.ylabel("İçerik Sayısı")
plt.legend()
plt.grid(True)
# plt.show()

#süreye göre tür analizi
print(df_netflix["duration"].head(20))

def parse_duration(duration):
    if pd.isna(duration) or duration == 0:
        return 0
    duration = str(duration)
    if 'min' in duration:
        return int(duration.replace('min', ''))
    elif 'Season' in duration:
        return int(duration.split(' ')[0])
    else:
        return 0
#yeni numeric sütun
df_netflix['duration_num'] = df_netflix['duration'].apply(parse_duration)

#kontrol: ilk 20 değer
print(df_netflix[["duration","duration_num"]].head(20))

#film ve dizi ayırma
df_movies = df_netflix[df_netflix["type"] == "Movie"]
df_tvshows = df_netflix[df_netflix["type"] == "TV Show"]

#kontrol
# print("Film sayısı:" , len(df_movies))
# print("Dizi Sayısı", len(df_tvshows))

#film türlerine göre ortalama süre

avg_duration_movies = {}
for cat in categories:
# o türdeki filmlerin duration_num ortalaması
    avg_duration_movies[cat] = df_movies[df_movies[cat]==1]["duration_num"].mean()

avg_duration_movies = pd.Series(avg_duration_movies).sort_values(ascending=False)
avg_duration_movies_int = avg_duration_movies.round(0).astype(int)
print("--- Film Türleri Ortalama Süre (Dakika) ---")
print(avg_duration_movies_int)

avg_duration_tv = {}
for cat in categories:
    avg_duration_tv[cat] = df_tvshows[df_tvshows[cat]==1]["duration_num"].mean()

avg_duration_tv =pd.Series(avg_duration_tv).sort_values(ascending=False)
avg_duration_tv_int = avg_duration_tv.fillna(0).round(0).astype(int)
print("--- TV Show Türleri Ortalama Süre (Sezon Sayısı) ---")
print(avg_duration_tv_int)

#film
plt.figure(figsize = (12,6))
avg_duration_movies_int.plot(kind="bar",color="skyblue")
plt.title("Film Türlerine Göre Ortalama Süre (Dakika)")
plt.xlabel("Tür")
plt.ylabel("Ortalama Dakika")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

#dizi
plt.figure(figsize = (12,6))
avg_duration_tv.plot(kind="bar",color="skyblue")
plt.title("Dizi Türlerine Göre Ortalama Süre (Sezon)")
plt.xlabel("Tür")
plt.ylabel("Ortalama Sezon")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()







