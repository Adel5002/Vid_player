from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


# Основная модель (таблица User)
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str


# Схемы (без таблиц)
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


# Связь многие-ко-многим между аниме и жанрами
class AnimeGenreLink(SQLModel, table=True):
    anime_id: Optional[int] = Field(default=None, foreign_key="anime.id", primary_key=True)
    genre_id: Optional[int] = Field(default=None, foreign_key="genre.id", primary_key=True)

# Таблица жанров
class Genre(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # Связь с аниме
    anime: List["Anime"] = Relationship(back_populates="genres", link_model=AnimeGenreLink)

class GenreCreate(SQLModel):
    name: str

class GenreRead(SQLModel):
    id: int
    name: str

# Основная таблица аниме
class Anime(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    kodik_id: str  # id аниме на Kodik
    player_link: str
    title: str
    title_orig: Optional[str]
    year: Optional[int]
    type: Optional[str]
    status: Optional[str]  # ongoing, released, etc.
    last_episode: Optional[int]
    last_season: Optional[int]
    created_at: datetime = Field(default_factory=None)
    updated_at: datetime = Field(default_factory=None)
    needs_update: bool = Field(default=True)

    # Связь с жанрами
    genres: List[Genre] = Relationship(back_populates="anime", link_model=AnimeGenreLink)

    # Связь с постером
    poster: Optional["AnimePoster"] = Relationship(back_populates="anime", sa_relationship_kwargs={"uselist": False})

class AnimeCreate(SQLModel):
    kodik_id: str
    player_link: str
    title: str
    title_orig: Optional[str]
    year: Optional[int]
    type: Optional[str]
    status: Optional[str]
    last_episode: Optional[int]
    last_season: Optional[int]
    created_at: datetime = Field(default_factory=None)
    updated_at: datetime = Field(default_factory=None)

    genres: Optional[List[GenreCreate]] = None
    poster: Optional['AnimePosterCreate'] = None

class AnimeRead(SQLModel):
    id: int
    kodik_id: str
    player_link: str
    title: str
    title_orig: Optional[str]
    year: Optional[int]
    type: Optional[str]
    status: Optional[str]
    last_episode: Optional[int]
    last_season: Optional[int]
    created_at: datetime
    updated_at: datetime

    genres: List[GenreRead] = []
    poster: Optional['AnimePosterRead'] = None



class AnimePoster(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    anime_id: Optional[int] = Field(default=None, foreign_key="anime.id")
    shikimori_id: Optional[int] = Field(unique=True, default=None)
    shikimori_image_link: Optional[str] = None
    kinopoisk_id: Optional[int] = Field(unique=True, default=None)
    worldart_link: Optional[str] = None
    local_image_link: Optional[str] = None

    anime: Optional[Anime] = Relationship(back_populates="poster")

class AnimePosterCreate(SQLModel):
    shikimori_id: Optional[int] = None
    shikimori_image_link: Optional[str] = None
    kinopoisk_id: Optional[int] = None
    worldart_link: Optional[str] = None
    local_image_link: Optional[str] = None


# READ: для ответа API (все поля + id)
class AnimePosterRead(SQLModel):
    id: int
    shikimori_id: Optional[int] = None
    shikimori_image_link: Optional[str] = None
    kinopoisk_id: Optional[int] = None
    worldart_link: Optional[str] = None
    local_image_link: Optional[str] = None


# UPDATE: частичное обновление (например, когда докачали постер)
class AnimePosterUpdate(SQLModel):
    shikimori_id: Optional[int] = None
    shikimori_image_link: Optional[str] = None
    kinopoisk_id: Optional[int] = None
    worldart_link: Optional[str] = None
    local_image_link: Optional[str] = None
