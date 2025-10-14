from typing import Optional, List

from pydantic import model_validator, field_serializer
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON
from sqlalchemy.types import TypeDecorator

# --- User ---
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    is_admin: Optional[bool] = Field(default=False)
    disabled: Optional[bool] = Field(default=True)
    is_verified: Optional[bool] = Field(default=False)
    profile: Optional["Profile"] = Relationship(
        back_populates="user",
        cascade_delete=True,
        sa_relationship_kwargs={
            "uselist": False
        }
    )


class UserCreate(SQLModel):
    username: str
    email: str
    password: str
    is_admin: Optional[bool] = Field(default=False)
    disabled: Optional[bool] = Field(default=True)
    is_verified: Optional[bool] = Field(default=False)


class UserRead(SQLModel):
    id: int
    username: str
    email: str
    is_admin: bool
    disabled: bool
    is_verified: bool
    profile: Optional["ProfileRead"]


class UserFrontendRead(SQLModel):
    id: int
    username: str
    profile: Optional["ProfileReadID"]

    @field_serializer("profile")
    def serialize_profile(self, profile):
        if profile is None:
            return None
        return profile.id

class UserUpdate(SQLModel):
    username: Optional[str] = Field(default=None)
    email: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)
    is_admin: Optional[bool] = Field(default=None)
    disabled: Optional[bool] = Field(default=True)
    is_verified: Optional[bool] = Field(default=None)


# --- Profile ---
class Profile(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="profile")
    watch_anime: List["WatchAnime"] = Relationship(
        back_populates="profile",
        cascade_delete=True
    )

class ProfileCreate(SQLModel):
    user_id: int
    watch_anime: Optional[List["WatchAnime"]] = []


class ProfileRead(SQLModel):
    id: int
    user_id: int
    watch_anime: Optional[List["WatchAnime"]] = []

class ProfileReadID(SQLModel):
    id: int


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


# --- WatchAnime ---
class WatchAnime(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    seek: int
    episode: int
    season: int
    finished: bool = Field(default=False)
    translation: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    profile_id: int = Field(foreign_key="profile.id")
    profile: Optional[Profile] = Relationship(back_populates="watch_anime")

    anime_id: int = Field(foreign_key="anime.id")
    anime: Optional["Anime"] = Relationship(back_populates="watch_anime")

class WatchAnimeCreate(SQLModel):
    seek: int
    episode: int
    season: int
    translation: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    profile_id: int
    anime_id: int
    finished: bool = Field(default=False)

class WatchAnimeUpdate(SQLModel):
    seek: Optional[int] = Field(default=None)
    episode: Optional[int] = Field(default=None)
    season: Optional[int] = Field(default=None)
    finished: Optional[bool] = Field(default=False)
    translation: Optional[dict] = Field(default=None, sa_column=Column(JSON))

class WatchAnimeRead(SQLModel):
    id: int
    seek: int
    episode: int
    season: int
    finished: bool
    translation: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    profile_id: int
    anime_id: int
    anime: Optional["AnimeRead"]


# --- Genre ---
class AnimeGenreLink(SQLModel, table=True):
    anime_info_id: Optional[int] = Field(default=None, foreign_key="animeinfo.id", primary_key=True)
    genre_id: Optional[int] = Field(default=None, foreign_key="genre.id", primary_key=True)

class Genre(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = None
    russian: Optional[str] = None

    info: List["AnimeInfo"] = Relationship(back_populates="genres", link_model=AnimeGenreLink)

class GenreCreate(SQLModel):
    name: Optional[str] = None
    russian: Optional[str] = None

class GenreRead(SQLModel):
    id: Optional[int]
    name: Optional[str] = None
    russian: Optional[str] = None


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
        cascade_delete=True
    )

    info: Optional["AnimeInfo"] = Relationship(
        back_populates="anime",
        sa_relationship_kwargs={"uselist": False},
        cascade_delete=True
    )

    watch_anime: List[WatchAnime] = Relationship(
        back_populates="anime",
        cascade_delete=True
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
    watch_anime: List[WatchAnime] = []
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
    kodik_player_url: Optional[str] = Field(default=None)


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
    is_censored: Optional[bool] = False
    kodik_player_url: Optional[str] = Field(default=None)

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
    is_censored: Optional[bool] = False
    kodik_player_url: Optional[str] = None

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
