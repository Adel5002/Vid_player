from datetime import datetime, date
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from sqlalchemy.types import TypeDecorator

# --- User ---
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str


class UserCreate(SQLModel):
    username: str
    email: str
    password: str


class UserRead(SQLModel):
    id: int
    username: str
    email: str


class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


# --- Genre ---
class AnimeGenreLink(SQLModel, table=True):
    anime_info_id: Optional[int] = Field(default=None, foreign_key="animeinfo.id", primary_key=True)
    genre_id: Optional[int] = Field(default=None, foreign_key="genre.id", primary_key=True)


class Genre(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = None

    info: List["AnimeInfo"] = Relationship(back_populates="genres", link_model=AnimeGenreLink)


class GenreCreate(SQLModel):
    name: Optional[str] = None


class GenreRead(SQLModel):
    id: Optional[int]
    name: Optional[str] = None


# --- Anime ---
class Anime(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    shikimori_id: Optional[int] = Field(default=None, unique=True)
    name: Optional[str] = None
    russian: Optional[str] = None
    url: Optional[str] = None
    kind: Optional[str] = None
    score: Optional[str] = None
    status: Optional[str] = None
    episodes: Optional[int] = 0
    episodes_aired: Optional[int] = 0
    aired_on: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    released_on: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    season: Optional[str] = None

    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    poster: Optional["AnimePoster"] = Relationship(
        back_populates="anime",
        sa_relationship_kwargs={"uselist": False},
    )

    info: Optional["AnimeInfo"] = Relationship(
        back_populates="anime",
        sa_relationship_kwargs={"uselist": False},
    )


class AnimeCreate(SQLModel):
    shikimori_id: Optional[int] = None
    name: Optional[str] = None
    russian: Optional[str] = None
    url: Optional[str] = None
    kind: Optional[str] = None
    score: Optional[str] = None
    status: Optional[str] = None
    episodes: Optional[int] = 0
    episodes_aired: Optional[int] = 0
    aired_on: Optional[dict] = None
    released_on: Optional[dict] = None
    poster: Optional["AnimePosterCreate"] = None
    info: Optional["AnimeInfoCreate"] = None
    season: Optional[str] = None

    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AnimeRead(SQLModel):
    id: Optional[int] = None
    shikimori_id: Optional[int] = None
    name: Optional[str] = None
    russian: Optional[str] = None
    url: Optional[str] = None
    kind: Optional[str] = None
    score: Optional[str] = None
    status: Optional[str] = None
    episodes: Optional[int] = 0
    episodes_aired: Optional[int] = 0
    aired_on: Optional[dict] = None
    released_on: Optional[dict] = None
    poster: Optional["AnimePosterRead"] = None
    info: Optional["AnimeInfoRead"] = None
    season: Optional[str] = None

    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# --- JSON Helper ---
class CleanJSONList(TypeDecorator):
    impl = JSON

    def process_bind_param(self, value, dialect):
        if not value:
            return None
        result = [x for x in value if x is not None]
        return None if len(result) == 0 else result

    def process_result_value(self, value, dialect):
        if not value:
            return None
        result = [x for x in value if x is not None]
        return None if len(result) == 0 else result


# --- AnimeInfo ---
class AnimeInfo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    anime_id: int = Field(foreign_key="anime.id", unique=True)
    shikimori_id: Optional[int] = Field(default=None, unique=True)

    rating: Optional[str] = None
    english: Optional[str] = Field(default=None)
    japanese: Optional[str] = Field(default=None)
    synonyms: Optional[List] = Field(default=None, sa_column=Column(CleanJSONList))
    license_name_ru: Optional[str] = None
    duration: Optional[int] = 0
    description: Optional[str] = None
    description_html: Optional[str] = None
    description_source: Optional[str] = None
    next_episode_at: Optional[str] = None
    fansubbers: Optional[List] = Field(default=None, sa_column=Column(CleanJSONList))
    fandubbers: Optional[List] = Field(default=None, sa_column=Column(CleanJSONList))
    licensors: Optional[List] = Field(default=None, sa_column=Column(CleanJSONList))
    studios: Optional[List] = Field(default=None, sa_column=Column(CleanJSONList))
    videos: Optional[List] = Field(default=None, sa_column=Column(CleanJSONList))
    screenshots: Optional[List] = Field(default=None, sa_column=Column(JSON))
    is_censored: Optional[bool] = False


    anime: Optional["Anime"] = Relationship(back_populates="info", sa_relationship_kwargs={"uselist": False})
    genres: Optional[List["Genre"]] = Relationship(back_populates="info", link_model=AnimeGenreLink)


class AnimeInfoCreate(SQLModel):
    anime_id: int
    shikimori_id: Optional[int] = None
    rating: Optional[str] = None
    english: Optional[str] = None
    japanese: Optional[str] = None
    synonyms: Optional[List] = None
    license_name_ru: Optional[str] = None
    duration: Optional[int] = 0
    description: Optional[str] = None
    description_html: Optional[str] = None
    description_source: Optional[str] = None
    next_episode_at: Optional[str] = None
    fansubbers: Optional[List] = None
    fandubbers: Optional[List] = None
    licensors: Optional[List] = None
    studios: Optional[List] = None
    videos: Optional[List] = None
    screenshots: Optional[List] = None
    genres: Optional[List["GenreCreate"]] = None


class AnimeInfoRead(SQLModel):
    id: int
    anime_id: int
    shikimori_id: Optional[int] = None
    rating: Optional[str] = None
    english: Optional[str] = None
    japanese: Optional[str] = None
    synonyms: Optional[List] = None
    license_name_ru: Optional[str] = None
    duration: Optional[int] = 0
    description: Optional[str] = None
    description_html: Optional[str] = None
    description_source: Optional[str] = None
    next_episode_at: Optional[str] = None
    fansubbers: Optional[List] = None
    fandubbers: Optional[List] = None
    licensors: Optional[List] = None
    studios: Optional[List] = None
    videos: Optional[List] = None
    screenshots: Optional[List] = None

    genres: Optional[List["GenreRead"]] = None


# --- Poster ---
class AnimePoster(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    anime_id: Optional[int] = Field(default=None, foreign_key="anime.id")
    originalUrl: Optional[str] = None
    mainUrl: Optional[str] = None
    local_image_link: Optional[str] = None

    anime: Optional["Anime"] = Relationship(back_populates="poster")


class AnimePosterCreate(SQLModel):
    anime_id: Optional[int] = None
    originalUrl: Optional[str] = None
    mainUrl: Optional[str] = None
    local_image_link: Optional[str] = None


class AnimePosterRead(SQLModel):
    id: int
    anime_id: Optional[int] = None
    originalUrl: Optional[str] = None
    mainUrl: Optional[str] = None
    local_image_link: Optional[str] = None


class AnimePosterUpdate(SQLModel):
    anime_id: Optional[int] = None
    originalUrl: Optional[str] = None
    mainUrl: Optional[str] = None
    local_image_link: Optional[str] = None
