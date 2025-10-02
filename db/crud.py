import datetime
from typing import Optional, List

from fastapi import HTTPException
from numpy.random.mtrand import Sequence
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
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
    anime = Anime(**anime_data.model_dump(exclude={"poster"}))
    try:
        session.add(anime)
        session.commit()
    except IntegrityError:
        session.rollback()
        anime = session.query(Anime).filter_by(shikimori_id=anime_data.shikimori_id).first()

    # постер
    if anime_data.poster:
        poster = AnimePoster(
            anime_id=anime.id,
            originalUrl=anime_data.poster.originalUrl,
            mainUrl=anime_data.poster.mainUrl,
            local_image_link=anime_data.poster.local_image_link,
        )
        session.merge(poster)
        session.commit()
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
    return session.scalars(select(Anime).where(Anime.shikimori_id == shikimori_id)).first()


from sqlalchemy import case, select, desc
from sqlalchemy.orm import selectinload
import datetime
from typing import Sequence

def get_anime_bulk(session: Session) -> Sequence[Anime]:
    current_year = str(datetime.date.today().year)

    # порядок сортировки: ongoing → released → anons
    status_order = case(
        (Anime.status == "ongoing", 0),
        (Anime.status == "released", 1),
        (Anime.status == "anons", 2),
        else_=3,
    )

    anime = session.scalars(
        select(Anime)
        .order_by(status_order, desc(Anime.score))
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
                created_at=item.created_at,
                updated_at=item.updated_at,
            ).model_dump()
        )

    return result




def get_anime_by_id(anime_id: int, session: Session) -> Anime:
    anime = session.scalar(select(Anime).where(Anime.shikimori_id == anime_id))
    if not anime:
        raise HTTPException(404, 'Anime does not exists')


    anime = AnimeRead(
            id=anime.id,
            shikimori_id=anime.shikimori_id,
            name=anime.name,
            russian=anime.russian,
            url=anime.url,
            kind=anime.kind,
            score=anime.score,
            status=anime.status,
            episodes=anime.episodes,
            episodes_aired=anime.episodes_aired,
            aired_on=anime.aired_on,
            released_on=anime.released_on,
            poster=anime.poster,
            info=anime.info,
            season=anime.season,
        )

    return anime


def update_anime(session: Session, anime_id: int, anime_data: AnimeCreate) -> Anime:
    anime = session.get(Anime, anime_id)
    if not anime:
        raise HTTPException(404, 'Anime does not exists')

    for field, value in anime_data.dict(exclude_unset=True).items():
        setattr(anime, field, value)

    session.add(anime)
    session.commit()
    session.refresh(anime)
    return anime


def get_all_possible_anime(session: Session) -> Sequence[Anime]:
    return session.scalars(select(Anime)).all()


def delete_anime(session: Session, anime_id: int) -> bool:
    anime = session.get(Anime, anime_id)
    if not anime:
        return False
    session.delete(anime)
    session.commit()
    return True


# ------------------ Anime Info ------------------
def create_anime_info(session: Session, info_data: AnimeInfoCreate) -> AnimeInfo:
    # Проверяем, есть ли уже запись для этого anime_id
    anime_info = session.scalars(select(AnimeInfo).where(AnimeInfo.anime_id == info_data.anime_id)).first()

    if not anime_info:
        anime_info = AnimeInfo(**info_data.dict(exclude={"genres"}))
        session.add(anime_info)
        session.commit()
        session.refresh(anime_info)

    # Обрабатываем жанры
    if info_data.genres:
        for g in info_data.genres:
            # Проверяем, есть ли такой жанр в таблице Genre
            genre = session.scalars(select(Genre).where(Genre.name == g.name)).first()
            if not genre:
                genre = Genre(name=g.name)
                session.add(genre)
                session.commit()
                session.refresh(genre)

            # Проверяем, есть ли уже связь AnimeGenreLink
            link_exists = session.scalars(
                select(AnimeGenreLink)
                .where(AnimeGenreLink.anime_info_id == anime_info.id)
                .where(AnimeGenreLink.genre_id == genre.id)
            ).first()

            if not link_exists:
                link = AnimeGenreLink(anime_info_id=anime_info.id, genre_id=genre.id)
                session.add(link)

        session.commit()

    return anime_info


def read_anime_info(session: Session, anime_id: int) -> AnimeInfo:
    info = session.scalar(
        select(AnimeInfo)
        .where(AnimeInfo.id == anime_id)
    )
    if not info:
        raise HTTPException(404, "AnimeInfo not found")
    return info



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
