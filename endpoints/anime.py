import json
import datetime
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

from utils.graphql_requests import get_anime_list

load_dotenv()

router = APIRouter()

# ------------------ Constants ------------------
WORLDART_BASE = "http://www.world-art.ru"

SHIKIMORI_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
}


# ------------------ Dramatiq ------------------
broker = RedisBroker()
dramatiq.set_broker(broker)


@dramatiq.actor(max_retries=5, min_backoff=1000, max_backoff=30000)
def add_anime_to_db(data: dict):
    """Асинхронное добавление аниме в базу через Dramatiq."""
    originalUrl = data.get("poster", {}).get("originalUrl")
    mainUrl = data.get("poster", {}).get("mainUrl")

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
            score=str(data.get("score")),
            status=data.get("status"),
            episodes=data.get("episodes", 0),
            episodes_aired=data.get("episodes_aired", 0),
            aired_on=data.get("aired_on"),
            released_on=data.get("released_on"),
            season=data.get("season"),
            poster=AnimePosterCreate(
                originalUrl=originalUrl,
                mainUrl=mainUrl,
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



def filter_and_sort_anime(anime_list: list[Anime], season: str = None) -> list[dict]:
    anime_list = [i.model_dump() for i in anime_list]


    # 1. фильтруем только те, где season содержит текущий год
    if season:
        anime_list = [a for a in anime_list if season in (a.get("season") or "")]

    # 2. сортируем по score по убыванию
    anime_list = sorted(anime_list, key=lambda x: float(x.get("score")) or 0, reverse=True)

    # 3. сортируем по статусу: ongoing -> released -> anons
    status_order = {"ongoing": 0, "released": 1, "anons": 2}
    anime_list.sort(key=lambda x: status_order.get(x.get("status"), 99))

    return anime_list

@router.get("/get-all-anime")
async def get_all_anime(
        season: str = "",
        page: int = 1,
        limit: int = 50,
        session: Session = Depends(get_session)
):
    cache_key = f"anime:{season}:{page}:{limit}"
    cached = await cache.get(cache_key)
    if cached:
        print("⚡ Отдаю из кэша:", cache_key)
        return json.loads(cached)

    bulk_anime = get_anime_bulk(session)
    start, end = (page - 1) * limit, page * limit

    if len(bulk_anime) < page * limit:
        new_anime_list = []
        safe_response = await get_anime_list(limit=limit, page=page)
        if len(safe_response) < limit:
            raise HTTPException(404, "Last page reached")

        for item in safe_response:
            new_anime_list.append(item)
            anime_in_db = get_anime_by_shikimori_id(session, item.get("id"))
            if not anime_in_db:
                add_anime_to_db.send_with_options(args=(item,))

        anime_list = filter_and_sort_anime(bulk_anime + new_anime_list, season)
    else:
        anime_list = filter_and_sort_anime(bulk_anime, season)

    results = {"results": anime_list[start:end], "page": page, "limit": limit}

    await cache.set(cache_key, json.dumps(results), ex=300)  # кэш на 5 минут
    return results

