import asyncio
from datetime import date

import dramatiq

from sqlmodel import Session

from db.crud import create_anime_info, create_anime, get_anime_by_shikimori_id
from db.db import engine
from db.models import AnimeInfoCreate, AnimePosterCreate, AnimeCreate

from dramatiq_actors import dramatiq_settings
from redis_cache import cache
from utils.graphql_requests import get_anime_list


@dramatiq.actor
async def fill_db(season: str = f'{date.today().year}'):
    print("Пошла возня...")
    cache.set("DB_READY", "false")
    limit = 50

    for page in range(1, 30000):
        safe_response = await get_anime_list(page=page, limit=limit, season=season)

        # Сделать остановку по окончанию работы этого актера
        if not 'animes' in safe_response:
            print('ANIMESSS', safe_response)

        if not safe_response.get('animes'):
            print('ANIMESSS', safe_response)
            cache.set("DB_READY", "true")
            break

        await asyncio.sleep(1.2)
        for anime in safe_response.get('animes'):
            add_anime_to_db.send_with_options(args=(anime,))


async def add_anime_to_queue(animes: list[dict]) -> None:
    print("Таска взята в работу ✅")
    for anime in animes:
        add_anime_to_db.send(anime)
        await asyncio.sleep(1)

@dramatiq.actor(max_retries=5, min_backoff=1000, max_backoff=30000)
async def add_anime_to_db(anime_data: dict) -> None:
    """Актёр: добавляет 1 аниме в БД."""
    with Session(engine) as session:
        anime_in_db = get_anime_by_shikimori_id(anime_data.get("id"), session)

        if anime_in_db:
            return  # Уже есть в БД

        originalUrl = anime_data.get("poster", {}).get("originalUrl")
        mainUrl = anime_data.get("poster", {}).get("mainUrl")

        anime = AnimeCreate(
            name=anime_data.get("name"),
            shikimori_id=anime_data.get("id"),
            russian=anime_data.get("russian"),
            url=anime_data.get("url"),
            kind=anime_data.get("kind"),
            score=str(anime_data.get("score")),
            status=anime_data.get("status"),
            episodes=anime_data.get("episodes", 0),
            episodes_aired=anime_data.get("episodesAired", 0),
            aired_on=anime_data.get("airedOn"),
            released_on=anime_data.get("releasedOn"),
            season=anime_data.get("season"),
            created_at=anime_data.get("createdAt"),
            updated_at=anime_data.get("updatedAt"),
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
            description_html=anime_data.get("descriptionHtml"),
            next_episode_at=anime_data.get("nextEpisodeAt"),
            duration=anime_data.get("duration"),
            screenshots=anime_data.get("screenshots"),
            videos=anime_data.get("videos"),
            fansubbers=anime_data.get("fansubbers"),
            fandubbers=anime_data.get("fandubbers"),
            license_name_ru=anime_data.get("licenseNameRu"),
            licensors=anime_data.get("licensors"),
            studios=anime_data.get("studios"),
            genres=anime_data.get("genres"),
            is_censored=anime_data.get("isCensored"),
        )

        create_anime_info(session, anime_info_data)
        print(f"✅ Аниме добавлено: {anime_data.get('name')}")