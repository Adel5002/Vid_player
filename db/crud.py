import datetime
from typing import Optional, List

from fastapi import HTTPException
from numpy.random.mtrand import Sequence
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select, desc

from .models import (
    User, UserCreate, UserUpdate,
    Anime, AnimeCreate, AnimePoster, AnimePosterCreate,
    Genre, GenreCreate, AnimeGenreLink,
    AnimeInfo, AnimeInfoCreate, AnimeRead
)


# ------------------ User ------------------
def create_user(session: Session, user_data: UserCreate) -> User:
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=user_data.password  # TODO: хэшировать пароль
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user(session: Session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)


def get_user_by_username(session: Session, username: str) -> Optional[User]:
    return session.exec(select(User).where(User.username == username)).first()


def update_user(session: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    user = session.get(User, user_id)
    if not user:
        return None

    update_data = user_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key == "password":
            setattr(user, "hashed_password", value)  # TODO: хэшировать пароль
        else:
            setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, user_id: int) -> bool:
    user = session.get(User, user_id)
    if not user:
        return False
    session.delete(user)
    session.commit()
    return True


# ------------------ Anime ------------------
def create_anime(session: Session, anime_data: AnimeCreate) -> Anime:
    anime = Anime(**anime_data.dict(exclude={"poster"}))
    session.add(anime)
    session.commit()
    session.refresh(anime)

    if anime_data.poster:
        poster = AnimePoster(
            anime_id=anime.id,
            originalUrl=anime_data.poster.originalUrl,
            mainUrl=anime_data.poster.mainUrl,
            local_image_link=anime_data.poster.local_image_link,
        )
        session.add(poster)
        session.commit()
        session.refresh(poster)
        anime.poster = poster

    return anime


def read_anime(session: Session, anime_id: int) -> Anime:
    anime = session.get(Anime, anime_id)
    if not anime:
        raise HTTPException(404, "Anime not found")
    return anime


def get_anime_by_name(session: Session, name: str) -> Optional[Anime]:
    return session.exec(select(Anime).where(Anime.name == name)).first()


def get_anime_by_shikimori_id(session: Session, shikimori_id: int) -> Optional[Anime]:
    return session.exec(select(Anime).where(Anime.shikimori_id == shikimori_id)).first()


def get_anime_bulk(session: Session) -> Sequence[Anime]:
    current_year = str(datetime.date.today().year)
    anime = session.scalars(
        select(Anime)
        .order_by(desc(Anime.score))
        .options(
            selectinload(Anime.info),
            selectinload(Anime.poster)
        )
    ).all()

    result = []
    for item in anime:
        result.append(
                AnimeRead(
                id=item.id,
                shikimori_id=item.shikimori_id,
                name=item.name,
                russian=item.russian,
                url=item.url,
                kind=item.kind,
                score=item.score,
                status=item.status,
                episodes=item.episodes,
                episodes_aired=item.episodes_aired,
                aired_on=item.aired_on,
                released_on=item.released_on,
                poster=item.poster,
                info=item.info,
                season=item.season,
            )
        )
    return result


def update_anime(session: Session, anime_id: int, anime_data: AnimeCreate) -> Optional[Anime]:
    anime = session.get(Anime, anime_id)
    if not anime:
        return None

    for field, value in anime_data.dict(exclude_unset=True).items():
        setattr(anime, field, value)

    session.add(anime)
    session.commit()
    session.refresh(anime)
    return anime


def get_all_possible_anime(session: Session) -> Sequence[Anime]:
    return session.exec(select(Anime)).all()


def delete_anime(session: Session, anime_id: int) -> bool:
    anime = session.get(Anime, anime_id)
    if not anime:
        return False
    session.delete(anime)
    session.commit()
    return True


# ------------------ Anime Info ------------------
def create_anime_info(session: Session, info_data: AnimeInfoCreate) -> AnimeInfo:
    anime_info = AnimeInfo(**info_data.dict(exclude={"genres"}))
    session.add(anime_info)
    session.commit()
    session.refresh(anime_info)

    if info_data.genres:
        for g in info_data.genres:
            genre = session.exec(select(Genre).where(Genre.name == g.name)).first()
            if not genre:
                genre = Genre(name=g.name)
                session.add(genre)
                session.commit()
                session.refresh(genre)
            link = AnimeGenreLink(anime_info_id=anime_info.id, genre_id=genre.id)
            session.add(link)
        session.commit()

    return anime_info


def read_anime_info(session: Session, info_id: int) -> AnimeInfo:
    info = session.get(AnimeInfo, info_id)
    if not info:
        raise HTTPException(404, "AnimeInfo not found")
    return info


def get_anime_info_by_anime_id(session: Session, anime_id: int) -> Optional[AnimeInfo]:
    return session.exec(select(AnimeInfo).where(AnimeInfo.anime_id == anime_id)).first()


def update_anime_info(session: Session, info_id: int, info_data: AnimeInfoCreate) -> Optional[AnimeInfo]:
    info = session.get(AnimeInfo, info_id)
    if not info:
        return None

    for field, value in info_data.dict(exclude_unset=True).items():
        if field != "genres":
            setattr(info, field, value)

    session.add(info)
    session.commit()
    session.refresh(info)

    if info_data.genres:
        # удаляем старые связи
        old_links = session.exec(select(AnimeGenreLink).where(AnimeGenreLink.anime_info_id == info.id)).all()
        for link in old_links:
            session.delete(link)
        session.commit()

        # добавляем новые
        for g in info_data.genres:
            genre = session.exec(select(Genre).where(Genre.name == g.name)).first()
            if not genre:
                genre = Genre(name=g.name)
                session.add(genre)
                session.commit()
                session.refresh(genre)
            link = AnimeGenreLink(anime_info_id=info.id, genre_id=genre.id)
            session.add(link)
        session.commit()

    return info


def delete_anime_info(session: Session, info_id: int) -> bool:
    info = session.get(AnimeInfo, info_id)
    if not info:
        return False
    session.delete(info)
    session.commit()
    return True


def get_all_anime_info(session: Session) -> List[AnimeInfo]:
    return session.exec(select(AnimeInfo)).all()


# ------------------ Genre ------------------
def create_genre(session: Session, genre_data: GenreCreate) -> Genre:
    genre = Genre(name=genre_data.name)
    session.add(genre)
    session.commit()
    session.refresh(genre)
    return genre


def read_genre(session: Session, genre_id: int) -> Optional[Genre]:
    return session.get(Genre, genre_id)


# ------------------ Anime Poster ------------------
def create_anime_poster(session: Session, anime_id: int, poster_data: AnimePosterCreate) -> AnimePoster:
    poster = AnimePoster(
        anime_id=anime_id,
        originalUrl=poster_data.poster.originalUrl,
        mainUrl=poster_data.poster.mainUrl,
        local_image_link=poster_data.local_image_link,
    )
    session.add(poster)
    session.commit()
    session.refresh(poster)
    return poster


def read_anime_poster(session: Session, poster_id: int) -> Optional[AnimePoster]:
    return session.get(AnimePoster, poster_id)
