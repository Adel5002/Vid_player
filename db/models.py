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
    name: str

    info: List["AnimeInfo"] = Relationship(back_populates="genres", link_model=AnimeGenreLink)


class GenreCreate(SQLModel):
    name: str


class GenreRead(SQLModel):
    id: int
    name: str


# --- Anime ---
class Anime(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    shikimori_id: Optional[int] = Field(default=None, unique=True)
    name: str
    russian: Optional[str] = None
    url: str
    kind: Optional[str] = None
    score: Optional[str] = None
    status: Optional[str] = None
    episodes: int = 0
    episodes_aired: int = 0
    aired_on: Optional[date] = None
    released_on: Optional[date] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    poster: Optional["AnimePoster"] = Relationship(back_populates="anime", sa_relationship_kwargs={"uselist": False})
    info: Optional["AnimeInfo"] = Relationship(back_populates="anime", sa_relationship_kwargs={"uselist": False})


class AnimeCreate(SQLModel):
    shikimori_id: Optional[int] = None
    name: str
    russian: Optional[str] = None
    url: str
    kind: Optional[str] = None
    score: Optional[str] = None
    status: Optional[str] = None
    episodes: int = 0
    episodes_aired: int = 0
    aired_on: Optional[date] = None
    released_on: Optional[date] = None
    poster: Optional["AnimePosterCreate"] = None


class AnimeRead(SQLModel):
    id: int
    shikimori_id: Optional[int] = None
    name: str
    russian: Optional[str] = None
    url: str
    kind: Optional[str] = None
    score: Optional[str] = None
    status: Optional[str] = None
    episodes: int
    episodes_aired: int
    aired_on: Optional[date] = None
    released_on: Optional[date] = None
    poster: Optional["AnimePosterRead"] = None
    info: Optional["AnimeInfoRead"] = None


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
    english: Optional[List] = Field(default=None, sa_column=Column(CleanJSONList))
    japanese: Optional[List] = Field(default=None, sa_column=Column(CleanJSONList))
    synonyms: Optional[List] = Field(default=None, sa_column=Column(CleanJSONList))
    license_name_ru: Optional[str] = None
    duration: Optional[int] = 0
    description: Optional[str] = None
    description_html: Optional[str] = None
    description_source: Optional[str] = None
    franchise: Optional[str] = None
    favoured: Optional[bool] = False
    anons: Optional[bool] = False
    ongoing: Optional[bool] = False
    thread_id: Optional[int] = None
    topic_id: Optional[int] = None
    myanimelist_id: Optional[int] = None
    rates_scores_stats: Optional[List] = Field(default=None, sa_column=Column(CleanJSONList))
    rates_statuses_stats: Optional[List] = Field(default=None, sa_column=Column(CleanJSONList))
    next_episode_at: Optional[datetime] = None
    fansubbers: Optional[List] = Field(default=None, sa_column=Column(CleanJSONList))
    fandubbers: Optional[List] = Field(default=None, sa_column=Column(CleanJSONList))
    licensors: Optional[List] = Field(default=None, sa_column=Column(CleanJSONList))
    studios: Optional[List] = Field(default=None, sa_column=Column(CleanJSONList))
    videos: Optional[List] = Field(default=None, sa_column=Column(CleanJSONList))
    screenshots: Optional[List] = Field(default=None, sa_column=Column(JSON))
    user_rate: Optional[float] = None

    anime: Optional["Anime"] = Relationship(back_populates="info", sa_relationship_kwargs={"uselist": False})
    genres: List["Genre"] = Relationship(back_populates="info", link_model=AnimeGenreLink)


class AnimeInfoCreate(SQLModel):
    anime_id: int
    shikimori_id: Optional[int] = None
    rating: Optional[str] = None
    english: Optional[List] = None
    japanese: Optional[List] = None
    synonyms: Optional[List] = None
    license_name_ru: Optional[str] = None
    duration: Optional[int] = 0
    description: Optional[str] = None
    description_html: Optional[str] = None
    description_source: Optional[str] = None
    franchise: Optional[str] = None
    favoured: Optional[bool] = False
    anons: Optional[bool] = False
    ongoing: Optional[bool] = False
    thread_id: Optional[int] = None
    topic_id: Optional[int] = None
    myanimelist_id: Optional[int] = None
    rates_scores_stats: Optional[List] = None
    rates_statuses_stats: Optional[List] = None
    next_episode_at: Optional[datetime] = None
    fansubbers: Optional[List] = None
    fandubbers: Optional[List] = None
    licensors: Optional[List] = None
    studios: Optional[List] = None
    videos: Optional[List] = None
    screenshots: Optional[List] = None
    user_rate: Optional[float] = None
    genres: Optional[List["GenreCreate"]] = None


class AnimeInfoRead(SQLModel):
    id: int
    anime_id: int
    shikimori_id: Optional[int] = None
    rating: Optional[str] = None
    english: Optional[List] = None
    japanese: Optional[List] = None
    synonyms: Optional[List] = None
    license_name_ru: Optional[str] = None
    duration: Optional[int] = 0
    description: Optional[str] = None
    description_html: Optional[str] = None
    description_source: Optional[str] = None
    franchise: Optional[str] = None
    favoured: Optional[bool] = False
    anons: Optional[bool] = False
    ongoing: Optional[bool] = False
    thread_id: Optional[int] = None
    topic_id: Optional[int] = None
    myanimelist_id: Optional[int] = None
    rates_scores_stats: Optional[List] = None
    rates_statuses_stats: Optional[List] = None
    next_episode_at: Optional[datetime] = None
    fansubbers: Optional[List] = None
    fandubbers: Optional[List] = None
    licensors: Optional[List] = None
    studios: Optional[List] = None
    videos: Optional[List] = None
    screenshots: Optional[List] = None
    user_rate: Optional[float] = None
    genres: List["GenreRead"] = []


# --- Poster ---
class AnimePoster(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    anime_id: Optional[int] = Field(default=None, foreign_key="anime.id")
    shikimori_image_link: Optional[str] = None
    local_image_link: Optional[str] = None

    anime: Optional["Anime"] = Relationship(back_populates="poster")


class AnimePosterCreate(SQLModel):
    anime_id: Optional[int] = None
    shikimori_image_link: Optional[str] = None
    local_image_link: Optional[str] = None


class AnimePosterRead(SQLModel):
    id: int
    anime_id: Optional[int] = None
    shikimori_image_link: Optional[str] = None
    local_image_link: Optional[str] = None


class AnimePosterUpdate(SQLModel):
    anime_id: Optional[int] = None
    shikimori_image_link: Optional[str] = None
    local_image_link: Optional[str] = None
