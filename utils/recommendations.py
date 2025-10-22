import io
import json
import joblib
import numpy as np
from typing import List
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from db.models import Anime
from redis_cache import cache

# ─────────────────────────────────────────────
# 🧠 Локальный мини-кэш (в памяти)
# ─────────────────────────────────────────────
_CACHE = {
    "vectorizer": None,
    "anime_ids": None,
}

# ─────────────────────────────────────────────
# 📦 Сериализация / десериализация
# ─────────────────────────────────────────────
def serialize_obj(obj):
    buf = io.BytesIO()
    joblib.dump(obj, buf)
    return buf.getvalue()

def deserialize_obj(data):
    buf = io.BytesIO(data)
    return joblib.load(buf)

# ─────────────────────────────────────────────
# 🧩 Построение TF-IDF и кэширование
# ─────────────────────────────────────────────
def _build_tfidf(session: Session):
    """Создаёт TF-IDF вектора и кэширует их в Redis по одному."""
    print("⚙️ Перестраиваем TF-IDF векторы...")

    animes = (
        session.query(Anime)
        .filter(Anime.info != None)
        .all()
    )

    corpus = []
    anime_ids = []

    for a in animes:
        if not a.info:
            continue

        info = a.info
        text_parts = []

        # 🧠 Описание
        if info.description:
            text_parts.append(info.description)

        # 🎭 Жанры
        if info.genres:
            text_parts += [g.name for g in info.genres]
            text_parts += [g.russian for g in info.genres]

        # 🏢 Студии
        if info.studios:
            for s in info.studios:
                if isinstance(s, dict) and "name" in s:
                    text_parts.append(s["name"])

        # 📅 Сезон / тип
        if a.kind:
            text_parts.append(a.kind)
        if a.season:
            text_parts.append(a.season)

        corpus.append(" ".join(filter(None, text_parts)))
        anime_ids.append(a.shikimori_id)

    stop_words = [
        "это", "в", "на", "и", "о", "от", "к", "но", "за", "из", "для", "с",
        "а", "по", "под", "что", "как", "же", "так", "of", "the", "to", "in",
        "on", "with", "for", "is", "are", "was", "by", "about", "an", "at"
    ]

    vectorizer = TfidfVectorizer(max_features=5000, stop_words=stop_words)
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Кэшируем vectorizer и список ID
    cache.set("anime_rec_vectorizer", serialize_obj(vectorizer))
    cache.set("anime_rec_ids", json.dumps(anime_ids))
    _CACHE["vectorizer"] = vectorizer
    _CACHE["anime_ids"] = anime_ids

    # Каждый вектор отдельно
    for i, anime_id in enumerate(anime_ids):
        cache.set(f"anime_vec:{anime_id}", serialize_obj(tfidf_matrix[i].toarray()))

    print(f"💾 Сохранено {len(anime_ids)} векторов в Redis")

# ─────────────────────────────────────────────
# 📤 Загрузка из Redis
# ─────────────────────────────────────────────
def _load_vectorizer():
    vec_data = cache.get("anime_rec_vectorizer")
    ids_data = cache.get("anime_rec_ids")

    if not vec_data or not ids_data:
        return None, None

    vectorizer = deserialize_obj(vec_data)
    anime_ids = json.loads(ids_data)

    _CACHE["vectorizer"] = vectorizer
    _CACHE["anime_ids"] = anime_ids
    print("✅ TF-IDF vectorizer загружен из Redis")
    return vectorizer, anime_ids

# ─────────────────────────────────────────────
# 💡 Рекомендации
# ─────────────────────────────────────────────
def get_recommendations(anime_id: int, session: Session, top_n: int = 10) -> List[int]:
    """Рекомендации на основе TF-IDF и жанров."""
    vectorizer, anime_ids = _load_vectorizer()

    if vectorizer is None or anime_ids is None:
        _build_tfidf(session)
        vectorizer, anime_ids = _load_vectorizer()

    target_vec = cache.get(f"anime_vec:{anime_id}")
    if not target_vec:
        _build_tfidf(session)
        target_vec = cache.get(f"anime_vec:{anime_id}")
        if not target_vec:
            return []

    target_vec = deserialize_obj(target_vec)

    similarities = []
    for aid in anime_ids:
        if aid == anime_id:
            continue
        vec_data = cache.get(f"anime_vec:{aid}")
        if not vec_data:
            continue
        vec = deserialize_obj(vec_data)
        sim = float(cosine_similarity(target_vec, vec))
        similarities.append((aid, sim))

    similarities.sort(key=lambda x: x[1], reverse=True)
    top = [aid for aid, _ in similarities[:top_n]]
    return top

# ─────────────────────────────────────────────
# 🔄 Обновление одного аниме (без пересборки всего)
# ─────────────────────────────────────────────
def update_anime_vector(anime_id: int, session: Session):
    """Пересчитывает TF-IDF-вектор только для одного аниме."""
    vectorizer, anime_ids = _load_vectorizer()
    if not vectorizer:
        _build_tfidf(session)
        vectorizer, anime_ids = _load_vectorizer()

    anime = session.query(Anime).filter(Anime.shikimori_id == anime_id).first()
    if not anime or not anime.info:
        print(f"⚠️ Anime {anime_id} не найден или без info")
        return

    info = anime.info
    text_parts = []

    if info.description:
        text_parts.append(info.description)
    if info.genres:
        text_parts += [g.name for g in info.genres]
        text_parts += [g.russian for g in info.genres]
    if info.studios:
        for s in info.studios:
            if isinstance(s, dict) and "name" in s:
                text_parts.append(s["name"])
    if anime.kind:
        text_parts.append(anime.kind)
    if anime.season:
        text_parts.append(anime.season)

    text = " ".join(filter(None, text_parts))
    vector = vectorizer.transform([text])
    cache.set(f"anime_vec:{anime_id}", serialize_obj(vector.toarray()))

    # если нового id нет в списке — добавим
    if anime_id not in _CACHE.get("anime_ids", []):
        anime_ids.append(anime_id)
        cache.set("anime_rec_ids", json.dumps(anime_ids))
        _CACHE["anime_ids"] = anime_ids

    print(f"✅ Вектор для {anime_id} обновлён")

# ─────────────────────────────────────────────
# 🧹 Очистка кэша
# ─────────────────────────────────────────────
def clear_recommendation_cache():
    """Полная очистка Redis-кэша рекомендаций."""
    for key in cache.scan_iter("anime_rec_*"):
        cache.delete(key)
    for key in cache.scan_iter("anime_vec:*"):
        cache.delete(key)
    _CACHE["vectorizer"] = None
    _CACHE["anime_ids"] = None
    print("🧹 Кэш рекомендаций очищен")
