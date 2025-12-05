import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3

#VERİYİ VERİTABANINDAN ÇEK
conn = sqlite3.connect("netflix.db")
df_netflix = pd.read_sql_query("SELECT * FROM netflix WHERE listed_in IS NOT NULL;", conn)
conn.close()

# EKSİK DEĞERLERİ TEMİZLE
df_netflix["description"] = df_netflix["description"].fillna("")
df_netflix["listed_in"] = df_netflix["listed_in"].fillna("")

#Açıklama + Tür metnini birleştir → TF-IDF için anlamlı metin
df_netflix["combined"] = df_netflix["description"] + " " + df_netflix["listed_in"]

# Film ve Dizileri Ayır (IMPORTANT: reset_index YAPMA!)
#  Çünkü df_netflix’teki gerçek satır indexine ihtiyacımız var.
df_movies = df_netflix[df_netflix["type"] == "Movie"].reset_index(drop=False) # index korunuyor
df_shows = df_netflix[df_netflix["type"] == "TV Show"] .reset_index(drop=False) # index korunuyor

#ORTAK TF-IDF MODELİ OLUŞTUR
#  Tüm içerikler aynı kelime uzayında vektörleşir.
tfidf_common = TfidfVectorizer(stop_words="english")
tfidf_matrix_common = tfidf_common.fit_transform(df_netflix["combined"])

# Film ve dizilerin ortak TF-IDF matristen satırlarını çek
# Burada df_movies.index → df_netflix’teki gerçek satır numarasıdır.
movie_indices = df_movies["index"]   # df_netflix’teki gerçek satır numarası
show_indices = df_shows["index"]

tfidf_movies_aligned = tfidf_matrix_common[movie_indices]
tfidf_shows_aligned = tfidf_matrix_common[show_indices]

#TÜM COSINE SIMILARITY MATRİSLERİ
# Film içinde benzerlik → Movie × Movie
cosine_sim_movies = cosine_similarity(tfidf_movies_aligned, tfidf_movies_aligned)
# Dizi içinde benzerlik → Show × Show
cosine_sim_shows = cosine_similarity(tfidf_shows_aligned, tfidf_shows_aligned)
# Film ↔ Dizi çapraz benzerlik → Movie × Show
cosine_sim_cross = cosine_similarity(tfidf_movies_aligned, tfidf_shows_aligned)

#GELİŞMİŞ ÖNERİ FONKSİYONU
def recommend(title):
    title = str(title).strip()
    result = f"Aradığınız içerik: {title}\n"

    film_list = []
    show_list = []

    # Kullanıcıdan alınan başlığı → index’e çevir
    idx_movies = pd.Series(df_movies.index, index=df_movies["title"])  # doğru
    idx_shows = pd.Series(df_shows.index, index=df_shows["title"])  # doğru
    # ARANAN FİLMSE
    if title in idx_movies.index:
        idx = idx_movies[title]  # film index
        # Film → Film önerisi
        scores = list(enumerate(cosine_sim_movies[idx]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:]  # kendisini çıkar
        # En çok benzeyen ilk 3 filmi seç
        top_films = scores[:3]
        film_list = [
            f"{df_movies.iloc[i]['title']} (Benzerlik: %{score * 100:.0f}, Süre: {df_movies.iloc[i]['duration']})"
            for i, score in top_films
        ]
        #Film → Dizi çapraz öneri
        cross_scores = list(enumerate(cosine_sim_cross[idx]))
        cross_scores = sorted(cross_scores, key=lambda x: x[1], reverse=True)

        # En iyi dizi skorunu kontrol et
        i, score = cross_scores[0]
        if score >= 0.15:
            show_list = [
                f"{df_shows.iloc[i]['title']} (Benzerlik: %{score * 100:.0f}, Süre: {df_shows.iloc[i]['duration']})"

            ]
    # ARANAN DİZİYSE
    elif title in idx_shows.index:
        idx = idx_shows[title]  # dizi index

        #Dizi → Dizi önerisi
        scores = list(enumerate(cosine_sim_shows[idx]))
        scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:]

        top_shows = scores[:3]
        show_list = [
            f"{df_shows.iloc[i]['title']} (Benzerlik: %{score * 100:.0f}, Süre: {df_shows.iloc[i]['duration']})"

            for i, score in top_shows
        ]
        #Dizi → Film çapraz öneri
        cross_scores = list(enumerate(cosine_sim_cross.T[idx]))
        cross_scores = sorted(cross_scores, key=lambda x: x[1], reverse=True)

        i, score = cross_scores[0]
        if score >= 0.15:
            film_list = [
                f"{df_movies.iloc[i]['title']} (Benzerlik: %{score * 100:.0f}, Süre: {df_movies.iloc[i]['duration']})"
            ]
    #Hiçbir kategoride bulunamadı
    else:
        return f"'{title}' adlı içerik veri setinde bulunamadı."

    #SONUÇ FORMATLAMA
    if film_list:
        result += "\nBenzer Filmler:\n"
        result += "\n".join("- " + f for f in film_list)

    if show_list:
        result += "\n\nBenzer Diziler:\n"
        result += "\n".join("- " + s for s in show_list)
    return result

#KULLANICI ARAYÜZÜ
if __name__ == "__main__":
    while True:
        user_input = input("Bir film veya dizi adı girin (çıkmak için b): ")

        if user_input.lower() == "b":
            print("Program kapatıldı.")
            break

        print("\n" + recommend(user_input))
        print("-" * 50)
