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
# print(df_netflix[["listed_in", "genre_group"]].head())


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

genre_counts = df_netflix[categories].sum().sort_values(ascending=False)
# print(genre_counts)

#grafik boyutları
# plt.figure(figsize = (12,6))
# #çubuk grafik
# plt.bar(genre_counts.index, genre_counts.values)

# #başlık ve etiketler
# plt.title("Netflix Tür Frekans Analizi")
# plt.xlabel("Türler")
# plt.ylabel("Frekans")
# plt.xticks(rotation=45, ha='right')

#grafiği götser
# plt.tight_layout()
# plt.show()


#sütunlar arasındaki kolerasyonu hesaplayarak, iki türün bir içerikte birlikte görülme sıklığını ölçebiliriz.
#kolerasyon matrisi hesaplama
#df_netflix'in sadece kategori sütunlarını kullanarak korelasyonu hesaplarız.Bu matris, türlerin birbiriyle ne kadar sık yan yana geldiğini gösterir.
# correlation_matrix = df_netflix[categories].corr()

# print("\n--- Türler Arası Korelasyon Matrisi ---")
# print(correlation_matrix)

# --- Isı Haritası Görselleştirmesi ---

# #grafik boyutunu ayarla
# plt.figure(figsize = (10,8))

# #ısı haritasını oluşturma
# sns.heatmap(
#     correlation_matrix, #hesaplanan korelasyon matrisi
#     annot=True, #korelasyon değerlerini hücrelerin içine yaz
#     fmt=".2f",           # Sayıları iki ondalık basamakla göster
#     cmap='coolwarm',     # Renk paleti: Mavi (Negatif) ve Kırmızı (Pozitif) ilişkileri ayırır.
#     linewidths=.5,       # Hücreler arasına çizgi ekle
#     cbar_kws={'label': 'Korelasyon Değeri'} # Renk çubuğu etiketi
# )
# #başlık ayarla
# plt.title("Netflix Türleri Arası Birliktelik (Korelasyon) Isı Haritası")
#
# #eksen ayarları
# plt.xticks(rotation=45, ha='right')
# plt.yticks(rotation=0)
# plt.tight_layout()
# # plt.show()

#kaç film birden fazla türe sahip
df_netflix["genre_count"] = df_netflix[categories].sum(axis=1)
multi_genre_counts = df_netflix["genre_count"].value_counts().sort_index()

# plt.figure(figsize = (8,5))
# plt.bar(multi_genre_counts.index, multi_genre_counts.values)
# plt.xlabel("Bir İçerikte Bulunan Tür Sayısı")
# plt.ylabel("İçerik Sayısı")
# plt.title("Netflix Çok Türlü İçeriklerin Dağılımı")
# plt.xticks(multi_genre_counts.index)
# #plt.show()#2 tür içeren içerikler en yaygın.1 tür ve3+ tür barındıran hemen hemen aynı düzeydedir. içerikler de oldukça fazla.3+ tür barındıran içerikler daha nadir.


#yıllara göre tür trendleri

# df_year_genre = df_netflix.groupby("release_year")[categories].sum()
# plt.figure(figsize = (14,6))
# plt.plot(df_year_genre.index, df_year_genre["Drama"])
# plt.title("YıılaraGöre Drama İçerik Sayıları")
# plt.xlabel("Yıl")
# plt.ylabel("Drama İçerik Sayısı")
# # plt.show()
#
# plt.figure(figsize = (14,7))
# for cat in categories:
#     plt.plot(df_year_genre.index, df_year_genre[cat],label=cat)

# plt.title("Yıllara Göre Netflix Tür Üretim Trendleri")
# plt.xlabel("Yıl")
# plt.ylabel("İçerik Sayısı")
# plt.legend()
# plt.grid(True)
# # plt.show()

#süreye göre tür analizi
# print(df_netflix["duration"].head(20))

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
# print(df_netflix[["duration","duration_num"]].head(20))

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
# print("--- Film Türleri Ortalama Süre (Dakika) ---")
# print(avg_duration_movies_int)

avg_duration_tv = {}
for cat in categories:
    avg_duration_tv[cat] = df_tvshows[df_tvshows[cat]==1]["duration_num"].mean()

avg_duration_tv =pd.Series(avg_duration_tv).sort_values(ascending=False)
avg_duration_tv_int = avg_duration_tv.fillna(0).round(0).astype(int)
# print("--- TV Show Türleri Ortalama Süre (Sezon Sayısı) ---")
# print(avg_duration_tv_int)

#film
# plt.figure(figsize = (12,6))
# avg_duration_movies_int.plot(kind="bar",color="skyblue")
# plt.title("Film Türlerine Göre Ortalama Süre (Dakika)")
# plt.xlabel("Tür")
# plt.ylabel("Ortalama Dakika")
# plt.xticks(rotation=45, ha='right')
# plt.tight_layout()
# # plt.show()

#dizi
# plt.figure(figsize = (12,6))
# avg_duration_tv.plot(kind="bar",color="skyblue")
# plt.title("Dizi Türlerine Göre Ortalama Süre (Sezon)")
# plt.xlabel("Tür")
# plt.ylabel("Ortalama Sezon")
# plt.xticks(rotation=45, ha='right')
# plt.tight_layout()
# # plt.show()

# ************************************************

#datframe her satırda 1 ülke içersin

#country kolonunu temizle
df_netflix['country'] = df_netflix['country'].fillna('Unknown')
df_netflix['country'] = df_netflix['country'].astype(str)
df_netflix['country'] = df_netflix['country'].replace("", "Unknown")

#ülke split + explode
df_netflix_country = df_netflix.assign(
    country=df_netflix['country'].str.split(', ')
).explode('country')
# print(df_netflix_country.head())
# print("\n--- COUNTRY EXPLODE SONRASI ---")
# print(df_netflix_country[['show_id', 'title', 'country']].head(20))

#en çok içerik üreten 10 ülke(film dizi karışık)
top10 = df_netflix_country['country'].value_counts().head(10)

plt.figure(figsize = (12,6))
sns.barplot(x=top10.values,y=top10.index)
plt.title("En çok içerik üreten ilk 10 ülke")
plt.xlabel("İçerik Sayısı")
plt.ylabel("Ülke")
# plt.show()

#film ve dizi ayrı ayrı ülke analizi
movies = df_netflix_country[df_netflix_country["type"] == "Movie"]
top10_movies = movies['country'].value_counts().head(10)
#diziler
shows = df_netflix_country[df_netflix_country["type"] == "TV Show"]
top10_shows = shows['country'].value_counts().head(10)
#yan yana grafik
fig, ax = plt.subplots(1,2,figsize=(12,6))
sns.barplot(x=top10_movies.values, y=top10_movies.index, ax=ax[0])
ax[0].set_title("En çok Film üreten Ülkeler")
ax[0].set_xlabel("Film Sayısı")

sns.barplot(x=top10_shows.values, y=top10_shows.index, ax=ax[1])
ax[1].set_title("En çok Dizi Üreten Ülkeler")
ax[1].set_xlabel("Dizi Sayısı")

# plt.tight_layout()
# plt.show()

#   ısı haritası

#ülke-tür matrisi
country_genre_matrix = df_netflix_country.pivot_table(
    index="country",
    values =categories, #drama,action vb tür
    aggfunc="sum"
)
#en çok içeriği olan ilk 10 ülke
top10_countries = df_netflix_country.country.value_counts().head(10).index
country_genre_top10 = country_genre_matrix.loc[top10_countries]

plt.figure(figsize = (14,6))
sns.heatmap(country_genre_top10, cmap="Reds", annot=True, fmt="d")
plt.title("En Çok İçerik Üreten İlk 10 Ülkenin Tür Dağılımı Isı Haritası")
plt.xlabel("Tür")
plt.ylabel("Ülke")
plt.tight_layout()
# plt.show()

#yönetmen başına içerik sayısı

#eksik yönetmenleri doldur
df_netflix['director'] = df_netflix['director'].fillna('Bilinmiyor')

#yönetmenleri listeye çevir
df_director = df_netflix.copy()
df_director['director'] = df_director['director'].str.split(', ')

#her yönetmeni aynı satıra aç
df_director = df_director.explode('director')

#yönetmen başına içerik sayısı
director_count = df_director['director'].value_counts().reset_index()
director_count.columns = ['director', 'content_count']

# print(director_count.head(10))
#Daha çok şöyle bir bilgi olur:
# “Veri setinde yönetmen bilgisi %X oranında eksik olduğu için yönetmen bazlı analiz sınırlıdır.”
# “Yine de mevcut veriler içinde en çok içerik üreten birkaç yönetmen şunlardır…”


#yönetmeni bilinmeyen içerikler hangi türlerde daha fazla

#unknown olanları filtrele
unknown_df = df_netflix[df_netflix['director'] == 'Unknown']
#listed_in sütununu explode et( zaten split edilmiş, ama explode gerekli
unknown_df_exploded = unknown_df.explode('listed_in')
#en çpk görülen türler(top10)
top_unknown_genres =unknown_df_exploded['listed_in'].value_counts().head(10)
# print("Yönetmeni bilinmeyen içeriklerde en çok görülen türler:")
# print(top_unknown_genres)

#grafik ile göster
plt.figure(figsize = (10,5))
sns.barplot(x=top_unknown_genres.values, y=top_unknown_genres.index,color="mediumseagreen")
plt.title("Yönetmeni Bilinmeyen İçeriklerde En Çok Görülen Türler")
plt.xlabel("İçerik Sayısı")
plt.ylabel("Tür")
plt.tight_layout()
# plt.show()

#Grafik veya tablo yorumunu buna göre açıkla:
# “Sadece yönetmen bilgisi olan içerikler üzerinden analiz yapılmıştır.”

#bilinmeyen yönetmenleri çıkar
df_known_directors = df_director[df_director['director'] != 'Unknown']
#her yönetmenin en çok içerik ürettiği türü bul
results = []
for director_name in df_known_directors['director'].unique():
    #bu yönetmenin tüm içerikleri
    director_contents = df_known_directors[df_known_directors['director'] == director_name]

    #tür bazında toplam içerik sayısı
    genre_counts = director_contents[categories].sum()

    #en çok içerik ürettiği tür
    top_genre = genre_counts.idxmax()
    count = genre_counts.max()

    results.append({
        'director': director_name,
        'top_genre': top_genre,
        'content_count': count,
    })
#dataframe oluştur
director_top_genre_df = pd.DataFrame(results)
#ilk 10 yönetmeni göster
# print(director_top_genre_df.sort_values(by='content_count', ascending=False).head(10))

#en çok içerik üreten 10 yönetmeni al
top10_directors = director_top_genre_df.sort_values('content_count', ascending=False).head(10)
top10_directors = top10_directors.sort_values('content_count', ascending=True)#yatay bar için


plt.figure(figsize = (12,6))
sns.barplot(
    x='content_count',
    y='director',
    data=top10_directors,
    hue='top_genre',  # sadece en yüksek tür
    dodge=False,  # tek bar
    palette="tab10"

)
#başlık ve etiketler
plt.title("Top 10 Yönetmenin En Çok Ürettiği Tür ve İçerik Sayısı")
plt.xlabel("İçerik Sayısı")
plt.ylabel("Yönetmen")
plt.legend(title="Top Tür")
# plt.tight_layout()
# plt.show()

#en popüler oyuncular
#bilinmeyen oyuncuları filtrele
df_known_cast = df_netflix[df_netflix['cast'] != 'Unknown']

#cast sütununu explode et
df_cast = df_known_cast.copy()
df_cast['cast'] = df_cast['cast'].str.split(',')
df_cast = df_cast.explode('cast')

#oyuncu başına içerik sayısı
cast_count = df_cast['cast'].value_counts().head(20)
# print(cast_count)

plt.figure(figsize = (12,6))
sns.barplot(x=cast_count.values,y=cast_count.index, color="mediumpurple")
plt.title("En Popüler İlk 20 Oyuncu (İçerik Sayısına Göre)")
plt.xlabel("İçerik Sayısı")
plt.ylabel("Oyuncu")
plt.tight_layout()
# plt.show()

#oyuncuların en çok oynadığı türler
results = []
for actor in df_cast['cast'].unique():
    actor_contents = df_cast[df_cast['cast'] == actor]
    genre_counts = actor_contents[categories].sum()
    top_genre = genre_counts.idxmax()
    count = genre_counts.max()
    results.append({
        'actor': actor,
        'top_genre': top_genre,
        'content_count': count,
    })
actor_top_genre_df = pd.DataFrame(results)
#en popüler 10 oyuncu al
top10_actors = actor_top_genre_df.sort_values('content_count', ascending=False).head(10)
top10_actors = top10_actors.sort_values('content_count', ascending=True)
# print(top10_actors)

plt.figure(figsize = (12,6))
sns.barplot(
    x='content_count',
    y='actor',
    data=top10_actors,
    hue='top_genre', dodge=False, palette="tab10"
)
plt.title("En Popüler 10 Oyuncu ve En Çok Yer Aldıkları Tür")
plt.xlabel("İçerik Sayısı")
plt.ylabel("Oyuncu")
plt.legend(title="Top Tür")
plt.tight_layout()
# plt.show()

# RATING ANALİZİ

# Rating boş alanları "Unknown" yap (0 kesinlikle kullanılmamalı!)
df_netflix["rating"] = df_netflix["rating"].fillna("Unknown")
df_netflix["rating"] = df_netflix["rating"].astype(str)

# Rating Dağılımı (Countplot)
plt.figure(figsize=(12, 6))
sns.countplot(
    x='rating',
    hue='rating',
    data=df_netflix,
    order=df_netflix['rating'].value_counts().index
)
plt.title('Netflix İçeriklerinin Rating Dağılımı')
plt.xlabel('Rating')
plt.ylabel('İçerik Sayısı')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# TÜRLERE GÖRE EN POPÜLER 10 TÜR (RATING DAĞILIMI)

df_rating = df_netflix.copy()

# Türleri explode et
df_rating['listed_in_split'] = df_rating['listed_in'].apply(
    lambda x: x if isinstance(x, list) else str(x).split(', ')
)
df_rating = df_rating.explode('listed_in_split')

# EN POPÜLER 10 tür
top10_genres = df_rating['listed_in_split'].value_counts().head(10).index

# popüler türlere filtre
df_top10 = df_rating[df_rating['listed_in_split'].isin(top10_genres)]

# pivot tablo: tür x rating
genre_rating_top10 = df_top10.pivot_table(
    index='listed_in_split',
    columns='rating',
    aggfunc='size',
    fill_value=0
)

# stacked bar chart
genre_rating_top10.plot(
    kind='bar',
    stacked=True,
    figsize=(14, 8),
    colormap='tab20'
)

plt.title("En Popüler 10 Türün Rating Dağılımı")
plt.xlabel("Tür")
plt.ylabel("İçerik Sayısı")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# YILLARA GÖRE RATING TRENDLERİ

df_recent = df_netflix[df_netflix['release_year'] >= 1990]

plt.figure(figsize=(14, 7))
sns.countplot(
    x='release_year',
    hue='rating',
    data=df_recent,
    palette="tab10"
)
plt.title('1990 Sonrası Yıllara Göre Rating Dağılımları')
plt.xlabel('Yıl')
plt.ylabel('İçerik Sayısı')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()





