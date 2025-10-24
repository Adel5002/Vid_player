import asyncio
import dramatiq
from sqlmodel import Session, select, or_

from db.db import engine
from db.models import Anime
from dramatiq_actors import dramatiq_settings
from utils.graphql_requests import search_for_anime


# ==============================
# 🧩 Нормализация данных от Shikimori
# ==============================
def normalize_shikimori_anime(shiki_data: dict) -> dict:
    """Преобразует структуру Shikimori в формат модели Anime."""
    anime = shiki_data

    return {
        "shikimori_id": int(anime["id"]),
        "name": anime.get("name"),
        "russian": anime.get("russian"),
        "url": anime.get("url"),
        "kind": anime.get("kind"),
        "score": float(anime.get("score", 0) or 0),
        "status": anime.get("status"),
        "episodes": anime.get("episodes"),
        "episodes_aired": anime.get("episodesAired"),
        "season": anime.get("season"),
        "aired_on": anime.get("airedOn", {}),
        "released_on": anime.get("releasedOn", {}),
        "poster": {
            "originalUrl": anime.get("poster", {}).get("originalUrl"),
            "mainUrl": anime.get("poster", {}).get("mainUrl"),
        },
        "info": {
            "rating": anime.get("rating"),
            "english": anime.get("english"),
            "japanese": anime.get("japanese"),
            "duration": anime.get("duration"),
            "description_html": anime.get("descriptionHtml"),
            "description": anime.get("description"),
            "studios": anime.get("studios", []),
            "videos": anime.get("videos", []),
            # genres можно не трогать, как ты сказал
        },
        "updated_at": anime.get("updatedAt"),
    }


# ==============================
# 🔁 Основная задача Dramatiq
# ==============================
@dramatiq.actor(queue_name="update_task")
async def update_ongoings():
    """Обновляет аниме со статусом 'ongoing' на основе данных Shikimori."""
    print("🚀 Начато обновление онгоингов...")

    updated_count = 0
    skipped = 0

    with Session(engine) as session:
        ongoings = session.scalars(select(Anime).where(or_(Anime.status == "ongoing", Anime.status == "anons"))).all()

        for anime in ongoings:
            try:
                raw_data = await search_for_anime(str(anime.shikimori_id))
                if not raw_data:
                    print(f"⚠️ Не удалось получить данные для {anime.name}")
                    skipped += 1
                    continue

                # В твоей версии search_for_anime возвращает список, поэтому берем [0]
                shiki = normalize_shikimori_anime(raw_data[0])

                has_changes = False

                # 🧩 Основные поля
                for field in ["status", "score", "episodes", "episodes_aired", "season", "kind", "name", "russian", "url", "released_on"]:
                    new_val = shiki.get(field)
                    if getattr(anime, field) != new_val:
                        setattr(anime, field, new_val)
                        has_changes = True

                # 🖼 Постер
                if anime.poster:
                    if anime.poster.mainUrl != shiki["poster"]["mainUrl"]:
                        anime.poster.mainUrl = shiki["poster"]["mainUrl"]
                        has_changes = True
                    if anime.poster.originalUrl != shiki["poster"]["originalUrl"]:
                        anime.poster.originalUrl = shiki["poster"]["originalUrl"]
                        has_changes = True

                # 📝 Информация
                if anime.info:
                    info = anime.info
                    shiki_info = shiki["info"]

                    for field in ["rating", "english", "japanese", "duration", "description_html", "description"]:
                        new_val = shiki_info.get(field)
                        if getattr(info, field) != new_val:
                            setattr(info, field, new_val)
                            has_changes = True

                    # 🎞 Видео
                    shiki_videos = shiki_info.get("videos", [])
                    if shiki_videos:
                        current_videos = getattr(info, "videos", [])
                        if len(current_videos) != len(shiki_videos) or {v["id"] for v in current_videos} != {v["id"] for v in shiki_videos}:
                            info.videos = shiki_videos
                            has_changes = True

                # 💾 Сохраняем, если есть изменения
                if has_changes:
                    anime.updated_at = shiki["updated_at"]
                    session.add(anime)
                    updated_count += 1
                    print(f"🔁 Обновлено: {anime.name}")
                else:
                    print(f"✅ Без изменений: {anime.name}")

                # 💤 Чтобы не бомбить Shikimori API
                await asyncio.sleep(0.7)

            except Exception as e:
                print(f"❌ Ошибка при обновлении {anime.name}: {e}")
                skipped += 1

        session.commit()

    print(f"🏁 Обновление завершено: {updated_count} обновлено, {skipped} пропущено.")
