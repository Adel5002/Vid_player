import asyncio
import json
import os
from enum import Enum

import re
from time import sleep

import dramatiq
import redis.asyncio as redis
from urllib.parse import urlparse, parse_qs, urljoin
from arq import create_pool
from arq.connections import RedisSettings
import requests
from bs4 import BeautifulSoup
from dramatiq.brokers.redis import RedisBroker

from fastapi import APIRouter
from fastapi.params import Depends
from sqlmodel import Session

from dotenv import load_dotenv

from db.crud import get_anime_by_kodik_id, get_anime_bulk, create_anime, get_all_possible_anime, get_anime_by_title
from db.db import get_session, engine
from db.models import AnimeCreate, AnimePosterCreate, AnimeRead

load_dotenv()

router = APIRouter()

class SortParameters(str, Enum):
    kinopoisk_rating = 'kinopoisk_rating'
    imdb_rating = 'imdb_rating'
    shikimori_rating = 'shikimori_rating'
    updated_at = "updated_at"

class OrderParameters(str, Enum):
    desc = 'desc'
    asc = 'asc'

WORLDART_BASE = "http://www.world-art.ru"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

shikimory_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
}

def get_anime_posters(poster_data):
    res = requests.get(
        f'https://api.jikan.moe/v4/anime/{poster_data
        ['shikimori_id']}/pictures',
        headers=shikimory_headers,
        timeout=4
    )
    res.raise_for_status()
    data = res.json()

    print('запрошен постер', data)
    for image in data.get('data'):
        if image.get('jpg').get('large_image_url'):
            poster_url = image.get('jpg').get('large_image_url')
            return poster_url
        elif image.get('jpg').get('image_url'):
            poster_url = image.get('jpg').get('image_url')
            return poster_url


def get_worldart_poster(page_url: str) -> str | None:
    """
    Возвращает абсолютный URL постера с world-art или None.
    page_url - ссылка на страницу, например:
      http://www.world-art.ru/animation/animation_poster.php?id=10964&number_img=1
    Функция сама сделает request, распарсит img теги и выберет наиболее подходящий.
    """
    try:
        # Если передали не poster-страницу, попытаться трансформировать:
        parsed = urlparse(page_url)
        qs = parse_qs(parsed.query)
        id_value = qs.get("id", [None])[0]
        number_img = qs.get("number_img", [None])[0]

        # Если не poster url, подменим animation.php -> animation_poster.php
        if "animation_poster" not in parsed.path and "animation.php" in parsed.path:
            poster_page = page_url.replace("animation.php", "animation_poster.php")
        else:
            poster_page = page_url

        resp = requests.get(poster_page, headers=HEADERS, timeout=6)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        imgs = []
        for img in soup.find_all("img"):
            src = img.get("src")
            if not src:
                continue
            # Нормализуем src: убираем ведущие ./ или ../
            src_norm = src.lstrip("./")
            # Собираем абсолютную ссылку (путь, начинающийся с img/... обычно относителен к корню)
            full_url = urljoin(WORLDART_BASE + "/animation/", src_norm)
            width = None
            try:
                width_attr = img.get("width")
                if width_attr:
                    width = int(width_attr)
            except Exception:
                width = None
            alt = img.get("alt", "")
            imgs.append({"src": src_norm, "full": full_url, "width": width, "alt": alt})

        # 1) Попробовать строгое совпадение по id и по номеру изображения (если задан number_img)
        if id_value:
            imgs_with_id = [i for i in imgs if f"/{id_value}/" in i["src"] or f"/{id_value}_" in i["src"]]
            if number_img:
                # ищем файл, заканчивающийся на /{number_img}.jpg или _{number_img}.jpg
                for c in imgs_with_id:
                    m = re.search(r'([/_])(\d+)\.(jpe?g|png)$', c["src"])
                    if m and m.group(2) == number_img:
                        return c["full"]
            # если не нашли точного номера — взять самый "широкий" вариант с этим id
            if imgs_with_id:
                imgs_with_id.sort(key=lambda x: (x["width"] or 0), reverse=True)
                return imgs_with_id[0]["full"]

        # 2) Выбрать любое изображение с большим width (>=600)
        large = [c for c in imgs if c["width"] and c["width"] >= 600]
        if large:
            # возвращаем первое крупное
            return large[0]["full"]

        # 3) Выбрать первое изображение в папке /img/
        for c in imgs:
            if "/img/" in c["src"] or c["src"].startswith("img/"):
                return c["full"]

        # 4) Иначе вернуть первый найденный img (если есть)
        if imgs:
            return imgs[0]["full"]

        return None

    except Exception as exc:
        # Логируй по необходимости
        # print("WorldArt parse error:", exc)
        return None

def unique_by_title(results):
    seen = set()
    unique = []
    for item in results:
        title = item.get("title")
        if title not in seen:
            seen.add(title)
            unique.append(item)
    return unique


async def get_anime_list(
    year: str | None = None,
    sort: SortParameters = SortParameters.shikimori_rating,
    order: OrderParameters = OrderParameters.desc,
    next_page: str | None = None,
    prev_page: str | None = None,
    limit: int = 40
):

    voices_id = ','.join(map(str, [3861, 609, 1068, 767, 739, 643, 1002]))

    endpoint = (
        f"{os.getenv('GET_ALL_SERIALS')}"
        f"?token={os.getenv('KODIK_API_KEY')}"
        f"&types=anime,anime-serial"
        f"&sort={sort.value}"
        f"&order={order.value}"
        f"&with_episodes=false"
        f"&with_seasons=false"
        f"&limit={limit}"
        f"&translation_id={voices_id}"
    )

    if year:
        endpoint += f"&year={year}"
    if next_page:
        endpoint += f'&next={next_page}'
    elif prev_page:
        endpoint += f'&prev={prev_page}'

    response = requests.get(endpoint)
    response.raise_for_status()

    safe_response = {}
    for k, v in response.json().items():
        if k == "prev_page" and v:
            safe_response[k] = v.split("prev=")[1]
        elif k == "next_page" and v:
            safe_response[k] = v.split("next=")[1]
        else:
            safe_response[k] = v

    safe_response['results'] = unique_by_title(safe_response['results'])


    return safe_response


broker = RedisBroker()
dramatiq.set_broker(broker)

@dramatiq.actor()
def add_anime_to_db(data: dict):
    shikimori_poster_link = get_anime_posters(data)
    with Session(engine) as session:
        anime_data = AnimeCreate(
            kodik_id=data.get('id'),
            player_link=data.get('link'),
            title=data.get('title'),
            status=data.get('missing'),
            title_orig=data.get('title_orig'),
            year=data.get('year'),
            type=data.get('type'),
            last_episode=data.get('last_episode'),
            last_season=data.get('last_season'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            poster=AnimePosterCreate(
                shikimori_id=data.get('shikimori_id'),
                shikimori_image_link=shikimori_poster_link,
                kinopisk_id=data.get('kinopisk_id'),
                worldart_link=data.get('worldart_link'),
            )
        )
        create_anime(session, anime_data)
        print('Создал новое аниме')

    sleep(3)

cache = redis.Redis(host='localhost', port=6379, db=0)

@router.get('/get-all-possible-anime/', response_model=list[AnimeRead])
async def get_full_anime_list(session: Session = Depends(get_session)):
    async for key in cache.scan_iter("*"):
        value = cache.get(key)
        print('значение ',value)
    return get_all_possible_anime(session)

@router.get('/get-all-anime')
async def get_all_anime(page: int = 1, limit: int = 40, session: Session = Depends(get_session)):
    cached = await cache.get(str(page))
    if cached:
        return {"results": json.loads(cached), "page": page, "limit": limit}
    else:
        bulk_anime = get_anime_bulk(session, (page - 1) * limit, page * limit)

        if len(bulk_anime) < limit:
            next_page = None
            new_anime_list = []
            anime_cnt = limit - len(bulk_anime)
            while len(new_anime_list) < anime_cnt:
                safe_response = await get_anime_list(limit=limit, next_page=next_page)
                for item in safe_response.get('results'):
                    anime_in_db = get_anime_by_kodik_id(session, item.get('id'))
                    same_title = get_anime_by_title(session, item.get('title'))
                    if not anime_in_db and not same_title:
                        new_anime_list.append(item)
                        add_anime_to_db.send_with_options(args=(item,))
                    # Вызываем get_anime_list до тех пор пока не найдем чем заполнить запрашиваемую страницу
                    # после чего формируем таску на добавление инфы об аниме и постере в бд,
                    # у каждой таски будет таймер 30 сек чтобы не спамить апишке
                    # также мы будем добавлять эти данные в кэш на 60 сек и само собой перед всем этим мы будем проверять
                    # на наличие этих данных в кэше
                    if len(new_anime_list) >= anime_cnt:
                        break

                next_page = safe_response.get('next_page')
                if not next_page:
                    break

            final_page = bulk_anime + new_anime_list[:anime_cnt]
            await cache.set(str(page), json.dumps(final_page), ex=300)
            return {"results": final_page, "page": page, "limit": limit}

        return {"results": bulk_anime, "page": page, "limit": limit}

        # Если нет данных в кэше булкой запрашиваем их в кол-во ограничении.
        # Если же нужных нет и в бд то терроризируем кодик до тех пор пока не достанем нужное колво аниме
        # Если же у нас сбросится кэш, что вполне может произойти и мы не на 1 странице, то нам потребуется заново
        # запросить все страницы, до той страницы, на которой мы находимся. Но в таком могут происходить разного рода
        # приколы, по типу что содержание предыдущих страниц может неожиданно поменяться, хотя я не думаю что на поздних
        # порах это будет проблемой так как бд уже будет достаточно хорошо заполнена а стандартную сортировку я буду
        # выполнять по updated_at который предоставляет кодик и по факту вызовы к кодик будет со временем делаться все
        # реже и реже



