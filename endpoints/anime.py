import json
import os
from time import sleep

import dramatiq
import redis.asyncio as redis
import requests
from dramatiq.brokers.redis import RedisBroker
from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session

from db.crud import (
    get_anime_bulk, create_anime, create_anime_info,
    get_all_possible_anime, get_anime_by_shikimori_id
)
from db.db import get_session, engine
from db.models import (
    AnimeCreate, AnimePosterCreate, AnimeRead,
    AnimeInfoCreate, Anime
)

load_dotenv()

router = APIRouter()

# ------------------ Constants ------------------
WORLDART_BASE = "http://www.world-art.ru"

SHIKIMORI_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
}

# ------------------ Shikimori API ------------------
async def get_anime_list(
    limit: int = 50,
    order: str = "popularity",
    status: str = "ongoing",
    page: int = 1
):
    endpoint = (
        f"{os.getenv('SHIKIMORI_API_V1')}/animes"
        f"?limit={limit}"
        f"&order={order}"
        f"&status={status}"
        f"&page={page}"
    )

    response = requests.get(endpoint, headers=SHIKIMORI_HEADERS, timeout=15)
    if response.status_code != 200:
        raise HTTPException(response.status_code, "Failed to fetch from Shikimori API")

    return response.json()


# ------------------ Dramatiq ------------------
broker = RedisBroker()
dramatiq.set_broker(broker)


@dramatiq.actor(max_retries=5, min_backoff=1000, max_backoff=30000)
def add_anime_to_db(data: dict):
    """Асинхронное добавление аниме в базу через Dramatiq."""
    poster_link = data.get("image", {}).get("original")

    # Запрос подробной информации
    url = f"https://shikimori.one/api/animes/{data.get('id')}"
    anime_data_req = requests.get(url, headers=SHIKIMORI_HEADERS, timeout=15)
    anime_data = anime_data_req.json()

    with Session(engine) as session:
        anime = AnimeCreate(
            name=data.get("name"),
            shikimori_id=data.get("id"),
            russian=data.get("russian"),
            url=data.get("url"),
            kind=data.get("kind"),
            score=data.get("score"),
            status=data.get("status"),
            episodes=data.get("episodes", 0),
            episodes_aired=data.get("episodes_aired", 0),
            aired_on=data.get("aired_on"),
            released_on=data.get("released_on"),
            poster=AnimePosterCreate(
                shikimori_image_link=poster_link,
                local_image_link=None,
            ),
        )

        anime = create_anime(session, anime)

        anime_info_data = AnimeInfoCreate(
            anime_id=anime.id,
            shikimori_id=anime_data.get("id"),
            rating=anime_data.get("rating"),
            english=anime_data.get("english"),
            japanese=anime_data.get("japanese"),
            synonyms=anime_data.get("synonyms"),
            description=anime_data.get("description"),
            description_html=anime_data.get("description_html"),
            franchise=anime_data.get("franchise"),
            duration=anime_data.get("duration"),
            ongoing=anime_data.get("ongoing"),
            thread_id=anime_data.get("thread_id"),
            topic_id=anime_data.get("topic_id"),
            myanimelist_id=anime_data.get("myanimelist_id"),
            screenshots=anime_data.get("screenshots"),
            rates_scores_stats=anime_data.get("rates_scores_stats"),
            rates_statuses_stats=anime_data.get("rates_statuses_stats"),
            videos=anime_data.get("videos"),
            fansubbers=anime_data.get("fansubbers"),
            fandubbers=anime_data.get("fandubbers"),
            license_name_ru=anime_data.get("license_name_ru"),
            licensors=anime_data.get("licensors"),
            studios=anime_data.get("studios"),
            genres=anime_data.get("genres"),
        )

        create_anime_info(session, anime_info_data)
        print(f"Аниме добавлено: {data.get('name')}")

    sleep(1)


# ------------------ Redis Cache ------------------
cache = redis.Redis(host="localhost", port=6379, db=0)


# ------------------ Routes ------------------
@router.get("/get-all-possible-anime/", response_model=list[AnimeRead])
async def get_full_anime_list(session: Session = Depends(get_session)):
    return get_all_possible_anime(session)


def anime_to_dict(anime: Anime) -> dict:
    """Сериализация ORM объекта в словарь с вложенными объектами"""
    return {
        "id": anime.id,
        "shikimori_id": anime.shikimori_id,
        "name": anime.name,
        "russian": anime.russian,
        "url": anime.url,
        "kind": anime.kind,
        "score": anime.score,
        "status": anime.status,
        "episodes": anime.episodes,
        "episodes_aired": anime.episodes_aired,
        "aired_on": anime.aired_on.isoformat() if anime.aired_on else None,
        "released_on": anime.released_on.isoformat() if anime.released_on else None,
        "poster": {
            "shikimori_image_link": anime.poster.shikimori_image_link if anime.poster else None,
            "local_image_link": anime.poster.local_image_link if anime.poster else None,
        } if anime.poster else None,
    }

@router.get("/get-all-anime")
async def get_all_anime(page: int = 1, limit: int = 50, session: Session = Depends(get_session)):
    cached = await cache.get(str(page))
    if cached:
        return {"results": json.loads(cached), "page": page, "limit": limit}


    bulk_anime = [anime_to_dict(a) for a in get_anime_bulk(session, (page - 1) * limit, page * limit)]

    if len(bulk_anime) < limit:
        
        next_page = page
        new_anime_list = []
        anime_cnt = limit - len(bulk_anime)

        while len(new_anime_list) < anime_cnt:
            safe_response = await get_anime_list(limit=limit, page=next_page)
            for item in safe_response:
                anime_in_db = get_anime_by_shikimori_id(session, item.get("id"))
                if not anime_in_db:
                    new_anime_list.append(item)
                    add_anime_to_db.send_with_options(args=(item,))

                if len(new_anime_list) >= anime_cnt:
                    break

            if len(safe_response) < limit:
                raise HTTPException(404, "Last page reached")

            next_page += 1

        final_page = bulk_anime + new_anime_list[:anime_cnt]
        await cache.set(str(page), json.dumps(final_page), ex=300)
        return {"results": final_page, "page": page, "limit": limit}

    return {"results": bulk_anime, "page": page, "limit": limit}
