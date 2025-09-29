import json
import logging

import redis.asyncio as redis
from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session

from db.crud import (
    get_anime_bulk, get_all_possible_anime, get_anime_by_shikimori_id, get_anime_by_id
)
from db.db import get_session
from db.models import AnimeRead, Anime

from dramatiq_actors.db_fill_actor import add_anime_to_db

from utils.graphql_requests import get_anime_list, search_for_anime
from utils.validate_anime_dict import validate_anime_dict


logging.basicConfig(level=logging.WARNING)

load_dotenv()

router = APIRouter()

# ------------------ Constants ------------------
WORLDART_BASE = "http://www.world-art.ru"

SHIKIMORI_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
}


# ------------------ Redis Cache ------------------
cache = redis.Redis(host="redis", port=6379, db=0)


# ------------------ Routes ------------------
@router.get("/get-all-possible-anime/", response_model=list[AnimeRead])
async def get_full_anime_list(session: Session = Depends(get_session)):
    return get_all_possible_anime(session)



def filter_and_sort_anime(anime_list: list[Anime], season: str = None) -> list[dict]:
    anime_list = [i.model_dump() if not isinstance(i, dict) else i for i in anime_list]

    # 1. фильтруем только те, где season содержит текущий год
    if season:
        anime_list = [a for a in anime_list if season in (a.get("season") or "")]

    # 2. сортируем по score по убыванию
    anime_list = sorted(anime_list, key=lambda x: float(x.get("score") or 0), reverse=True)

    # 3. сортируем по статусу: ongoing -> released -> anons
    status_order = {"ongoing": 0, "released": 1, "anons": 2}
    anime_list.sort(key=lambda x: status_order.get(x.get("status"), 99))

    return anime_list


# TODO: Разнести первичное заполнение бд и обновление бд по разным разделам.
# TODO: Пока бд заполняется ничего не сохранять в кэше как это происходит сейчас
# TODO: Обновление бд будет выполнено с помощью cron раз в день
# TODO: При получении новой записи полностью сбрасывать кэш и записывать его по новой
# TODO: При записывании кэша возможно стоит сделать так чтобы сначала загрузить в переменную все необходимые данные а в кэш записать уже нарезанные по страницам данные

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

    # Получаем все аниме из базы
    bulk_anime = get_anime_bulk(session)
    start, end = (page - 1) * limit, page * limit

    anime_list: list[dict] = []

    # Если в БД мало данных → тянем с API
    if len(bulk_anime) < page * limit:
        safe_response = await get_anime_list(limit=limit, page=page)

        async for key in cache.scan_iter("anime:*"):
            await cache.delete(key)

        if len(safe_response) < limit:
            raise HTTPException(404, "Last page reached")

        for item in safe_response:
            # Проверяем, есть ли уже такое аниме
            anime_in_db = get_anime_by_shikimori_id(session, item.get("id"))

            if not anime_in_db:
                # 🔹 Валидируем и добавляем в ответ пользователю
                anime_info_data = validate_anime_dict(item)
                anime_list.append(anime_info_data.model_dump())
                # 🔹 Отправляем задачу на запись в БД (асинхронно)
                add_anime_to_db.send_with_options(args=(item,))

        # Добавляем то, что уже было в БД
        anime_list = filter_and_sort_anime(bulk_anime + anime_list, season)

    else:
        # Если БД полная → используем только её
        anime_list = filter_and_sort_anime(bulk_anime, season)

    if len(anime_list) < page * limit:
        raise HTTPException(404, "Either the pages haven't been added to the database yet,"
                                 " or you need to update the cache.")

    results = {"results": anime_list[start:end], "page": page, "limit": limit}

    await cache.set(cache_key, json.dumps(results), ex=300)  # кэш на 5 минут
    return results




@router.get('/anime-watch/{anime_id}')
async def watch_anime(anime_id: int, session: Session = Depends(get_session)):
    try:
        anime_info = get_anime_by_id(anime_id, session)
        return anime_info
    except HTTPException:
        get_anime = await search_for_anime(str(anime_id))
        return validate_anime_dict(get_anime[0]).model_dump()