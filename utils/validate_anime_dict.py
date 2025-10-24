from db.models import AnimeCreate, AnimeInfoCreate, Anime, AnimePosterUpdate


def validate_anime_dict(item: dict) -> Anime:
    originalUrl = item.get("poster", {}).get("originalUrl")
    mainUrl = item.get("poster", {}).get("main2xUrl")
    anime = AnimeCreate(
        name=item.get("name"),
        shikimori_id=item.get("id"),
        russian=item.get("russian"),
        url=item.get("url"),
        kind=item.get("kind"),
        score=str(item.get("score")),
        status=item.get("status"),
        episodes=item.get("episodes", 0),
        episodes_aired=item.get("episodesAired", 0),
        aired_on=item.get("airedOn"),
        released_on=item.get("releasedOn"),
        season=item.get("season"),
        created_at=item.get("createdAt"),
        updated_at=item.get("updatedAt"),
        poster=AnimePosterUpdate(
            originalUrl=originalUrl,
            mainUrl=mainUrl,
            local_image_link=None,
        ),
        info=AnimeInfoCreate(
            anime_id=item.get("id"),
            shikimori_id=item.get("id"),
            rating=item.get("rating"),
            english=item.get("english"),
            japanese=item.get("japanese"),
            synonyms=item.get("synonyms"),
            description=item.get("description"),
            description_html=item.get("descriptionHtml"),
            next_episode_at=item.get("nextEpisodeAt"),
            duration=item.get("duration"),
            screenshots=item.get("screenshots"),
            videos=item.get("videos"),
            fansubbers=item.get("fansubbers"),
            fandubbers=item.get("fandubbers"),
            license_name_ru=item.get("licenseNameRu"),
            licensors=item.get("licensors"),
            studios=item.get("studios"),
            genres=item.get("genres"),
            kodik_player_url=item.get("kodik_player_url"),
            is_censored=item.get("isCensored"),
        )
    )

    return anime