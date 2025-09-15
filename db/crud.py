from typing import Optional

from fastapi import HTTPException
from sqlmodel import Session, select, desc
from .models import User, UserCreate, UserUpdate, AnimeCreate, Anime, AnimePoster, Genre, AnimeGenreLink, GenreCreate, \
    AnimePosterCreate


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


def get_user(session: Session, user_id: int) -> User | None:
    return session.get(User, user_id)


def get_user_by_username(session: Session, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()


def update_user(session: Session, user_id: int, user_data: UserUpdate) -> User | None:
    user = session.get(User, user_id)
    if not user:
        return None

    update_data = user_data.dict(exclude_unset=True)  # только переданные поля

    for key, value in update_data.items():
        if key == "password":
            # TODO: хэшировать пароль
            setattr(user, "hashed_password", value)
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


def create_anime(session: Session, anime_data: AnimeCreate) -> "Anime":

    # создаем аниме
    anime = Anime(
        kodik_id=anime_data.kodik_id,
        player_link=anime_data.player_link,
        title=anime_data.title,
        title_orig=anime_data.title_orig,
        year=anime_data.year,
        type=anime_data.type,
        status=anime_data.status,
        last_episode=anime_data.last_episode,
        last_season=anime_data.last_season,
        created_at=anime_data.created_at,
        updated_at=anime_data.updated_at,
    )
    session.add(anime)
    session.commit()
    session.refresh(anime)

    # создаем постер если есть
    if anime_data.poster:
        poster = AnimePoster(
            anime_id=anime.id,
            shikimori_id=anime_data.poster.shikimori_id,
            shikimori_image_link=anime_data.poster.shikimori_image_link,
            kinopoisk_id=anime_data.poster.kinopoisk_id,
            worldart_link=anime_data.poster.worldart_link,
            local_image_link=anime_data.poster.local_image_link,
        )
        session.add(poster)
        session.commit()
        session.refresh(poster)
        anime.poster = poster

    # создаем жанры
    if anime_data.genres:
        for g in anime_data.genres:
            # проверяем, есть ли уже такой жанр
            genre = session.exec(select(Genre).where(Genre.name == g.name)).first()
            if not genre:
                genre = Genre(name=g.name)
                session.add(genre)
                session.commit()
                session.refresh(genre)
            # связываем с аниме
            link = AnimeGenreLink(anime_id=anime.id, genre_id=genre.id)
            session.add(link)
        session.commit()

    return anime


def read_anime(session: Session, anime_id: int) -> Optional["Anime"]:
    anime = session.get(Anime, anime_id)
    if not anime:
        raise HTTPException(404, 'Anime not found')
    return anime


def get_anime_by_kodik_id(session: Session, kodik_id: int):
    anime = session.scalar(select(Anime).where(Anime.kodik_id == kodik_id))
    return anime

def get_anime_by_title(session: Session, title: str):
    anime = session.scalar(select(Anime).where(Anime.title == title))
    return anime

def get_anime_bulk(session: Session, offset: int, limit: int):
    bulk_anime = session.scalars(select(Anime).order_by(desc(Anime.updated_at)).offset(offset).limit(limit)).all()
    return bulk_anime


def update_anime(session: Session, anime_id: int, anime_data: AnimeCreate) -> Optional["Anime"]:
    anime = session.get(Anime, anime_id)
    if not anime:
        return None
    for field, value in anime_data.dict(exclude_unset=True).items():
        setattr(anime, field, value)
    session.add(anime)
    session.commit()
    session.refresh(anime)
    return anime

def get_all_possible_anime(session: Session):
    return session.scalars(select(Anime)).all()

def delete_anime(session: Session, anime_id: int) -> bool:
    anime = session.get(Anime, anime_id)
    if not anime:
        return False
    session.delete(anime)
    session.commit()
    return True


# ------------------ Genre ------------------
def create_genre(session: Session, genre_data: GenreCreate) -> "Genre":
    genre = Genre(name=genre_data.name)
    session.add(genre)
    session.commit()
    session.refresh(genre)
    return genre


def read_genre(session: Session, genre_id: int) -> Optional["Genre"]:
    return session.get(Genre, genre_id)


# ------------------ AnimePoster ------------------
def create_anime_poster(session: Session, anime_id: int, poster_data: AnimePosterCreate) -> "AnimePoster":
    poster = AnimePoster(
        anime_id=anime_id,
        shikimori_id=poster_data.shikimori_id,
        kinopoisk_id=poster_data.kinopoisk_id,
        worldart_link=poster_data.worldart_link,
        local_image_link=poster_data.local_image_link
    )
    session.add(poster)
    session.commit()
    session.refresh(poster)
    return poster


def read_anime_poster(session: Session, poster_id: int) -> Optional["AnimePoster"]:
    return session.get(AnimePoster, poster_id)
