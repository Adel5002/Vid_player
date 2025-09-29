from time import sleep

import dramatiq


from sqlmodel import Session

from db.crud import create_anime_info, create_anime
from db.db import engine
from db.models import AnimeInfoCreate, AnimePosterCreate, AnimeCreate


from dramatiq_actors import dramatiq_settings
@dramatiq.actor(max_retries=5, min_backoff=1000, max_backoff=30000)
def add_anime_to_db(data: dict):
    """Асинхронное добавление аниме в базу через Dramatiq."""
    originalUrl = data.get("poster", {}).get("originalUrl")
    mainUrl = data.get("poster", {}).get("mainUrl")

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
            aired_on=data.get("airedOn"),
            released_on=data.get("releasedOn"),
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
            shikimori_id=data.get("id"),
            rating=data.get("rating"),
            english=data.get("english"),
            japanese=data.get("japanese"),
            synonyms=data.get("synonyms"),
            description=data.get("description"),
            description_html=data.get("descriptionHtml"),
            duration=data.get("duration"),
            screenshots=data.get("screenshots"),
            videos=data.get("videos"),
            fansubbers=data.get("fansubbers"),
            fandubbers=data.get("fandubbers"),
            license_name_ru=data.get("licenseNameRu"),
            licensors=data.get("licensors"),
            studios=data.get("studios"),
            genres=data.get("genres"),
        )

        create_anime_info(session, anime_info_data)
        print(f"Аниме добавлено: {data.get('name')}")

    sleep(1)