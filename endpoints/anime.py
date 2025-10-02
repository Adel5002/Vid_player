import json
import logging

from dotenv import load_dotenv

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session

from db.crud import (
    get_anime_bulk, get_all_possible_anime, get_anime_by_id
)
from db.db import get_session
from db.models import AnimeRead, Anime
from redis_cache import cache

from utils.graphql_requests import search_for_anime
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
    cache_key = f"anime"
    cached = cache.get(cache_key)

    start, end = (page - 1) * limit, page * limit

    if cached:
        print("⚡ Отдаю из кэша:", cache_key)
        return json.loads(cached)[start:end]

    db_is_ready = cache.get("DB_READY")
    print(db_is_ready.decode("utf-8"))

    if db_is_ready.decode("utf-8") != "true":
        return {"status": "db is not ready yet, please wait..."}

    bulk_anime = get_anime_bulk(session)
    print(bulk_anime)
    cache.set('anime', json.dumps(bulk_anime))
    return bulk_anime[start:end]





@router.get('/anime-watch/{anime_id}')
async def watch_anime(anime_id: int, session: Session = Depends(get_session)):
    try:
        anime_info = get_anime_by_id(anime_id, session)
        return anime_info
    except HTTPException:
        get_anime = await search_for_anime(str(anime_id))
        return validate_anime_dict(get_anime[0]).model_dump()