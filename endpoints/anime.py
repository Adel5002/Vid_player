import asyncio
import json
import logging
from typing import Sequence, Union

from dotenv import load_dotenv

from fastapi import APIRouter, Depends
from sqlmodel import Session

from dramatiq_actors.db_fill_actor import add_anime_to_db, add_anime_to_queue

from db.crud import (
    get_anime_bulk, get_all_possible_anime, get_anime_by_shikimori_id, get_anime_by_name, delete_anime
)
from db.db import get_session
from db.models import AnimeRead, Anime
from kodik_api_calls.get_player_by_shiki_id import get_player_by_id
from redis_cache import cache

from utils.graphql_requests import search_for_anime
from utils.validate_anime_dict import validate_anime_dict


logging.basicConfig(level=logging.WARNING)

load_dotenv()

router = APIRouter()

# ------------------ Constants ------------------
SHIKIMORI_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
}



# ------------------ Routes ------------------
@router.get("/get-all-possible-anime/", response_model=Sequence[AnimeRead])
async def get_full_anime_list(session: Session = Depends(get_session)) -> Sequence[Anime]:
    return get_all_possible_anime(session)


# TODO: Придумать функционал обновления инфы об аниме если апи такого не предоставляет, а можно это сделать перебором
# TODO: аниме из моей бд и поиском их в бд шикимори
@router.get("/get-all-anime")
async def get_all_anime(
        season: str = "",
        page: int = 1,
        limit: int = 50,
        session: Session = Depends(get_session)
) -> Union[Sequence[dict], dict[str, str]]:
    cache_key = f"anime"
    cached = cache.get(cache_key)

    start, end = (page - 1) * limit, page * limit

    if cached:
        print("⚡ Отдаю из кэша:", cache_key)
        return json.loads(cached)[start:end]

    db_is_ready = cache.get("DB_READY")

    if db_is_ready is None or db_is_ready.decode("utf-8") != "true":
        return {"status": "db is not ready yet, please wait..."}

    bulk_anime = get_anime_bulk(session)
    cache.set('anime', json.dumps(bulk_anime), ex=300)
    return bulk_anime[start:end]


@router.get('/get-anime-by-name/{name}')
async def get_anime(name: str, session: Session = Depends(get_session)) -> Sequence[dict]:
    # 1️⃣ Пытаемся найти в БД
    from_db = get_anime_by_name(session, name)

    # 2️⃣ Собираем все известные названия из БД
    db_names = set()
    for a in from_db:
        if a.get("name"):
            db_names.add(a["name"].lower())
        if a.get("russian"):
            db_names.add(a["russian"].lower())

    # 3️⃣ Нормализуем запрос
    query_name = name.lower().strip()

    # 4️⃣ Определяем, нужно ли идти в API
    need_api = False

    if not from_db:
        # если вообще ничего нет в БД
        need_api = True
    else:
        exact_match = any(query_name == n for n in db_names)
        partial_match = any(query_name in n for n in db_names)

        # если нет совпадений вообще
        if not exact_match and not partial_match:
            need_api = True
        # если совпадение частичное и результатов мало
        elif partial_match and len(from_db) < 3:
            need_api = True

    # 5️⃣ Если нужно — ищем через API
    from_api = []
    if need_api:
        animes = await search_for_anime(anime_name=name)
        add_anime_to_queue.send(animes)

        validated = [validate_anime_dict(a).model_dump() for a in animes]

        # фильтруем дубликаты по имени и русскому названию
        from_api = [
            a for a in validated
            if a["name"].lower() not in db_names
            and (a.get("russian") or "").lower() not in db_names
        ]

    # 6️⃣ Возвращаем объединённый результат
    return [*from_db, *from_api]



@router.get('/watch-anime/{anime_id}')
async def watch_anime(anime_id: int, session: Session = Depends(get_session)) -> dict:
    anime_info = get_anime_by_shikimori_id(anime_id, session)

    if not anime_info:
        anime = await search_for_anime(str(anime_id))
        anime[0]["kodik_player_url"] = await get_player_by_id(anime[0].get("id", "none"))
        add_anime_to_db.send(anime[0])
        return validate_anime_dict(anime[0]).model_dump()
    return anime_info

@router.delete("/delete-anime/{anime_id}")
async def delete_anime_by_id(anime_id: int, session: Session = Depends(get_session)):
    return delete_anime(session, anime_id)
