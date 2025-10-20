from typing import Optional

from sqlalchemy import func, Integer
from sqlmodel import Session, select, cast, or_
from fastapi import Query
from pydantic import BaseModel

from db.models import Anime, Genre, AnimeGenreLink, AnimeInfo


class AnimeFilter(BaseModel):
    genre: Optional[str] = Query(None, description="Фильтр по жанру")
    year_start: Optional[int] = Query(None, description="Начальный год диапазона")
    year_end: Optional[int] = Query(None, description="Конечный год диапазона")
    status: Optional[str] = Query(None, description="Статус (released, ongoing, anons)")
    score_min: Optional[float] = Query(0, description="Минимальный рейтинг")


def filter_anime(
    filters: AnimeFilter,
    limit: int,
    session: Session
):
    # Извлекаем год из season ('fall_2023' -> 2023)
    year_expr = cast(
        func.nullif(func.regexp_replace(Anime.season, '[^0-9]', '', 'g'), ''), Integer
    )

    query = select(Anime).where(Anime.score >= filters.score_min)

    if filters.genre:
        query = (
            query.join(Anime.info)
            .join(AnimeGenreLink, AnimeInfo.id == AnimeGenreLink.anime_info_id)
            .join(Genre, Genre.id == AnimeGenreLink.genre_id)
            .where(or_(Genre.name == filters.genre, Genre.russian == filters.genre))
        )

    # 🎯 Диапазон годов
    if filters.year_start and filters.year_end:
        query = query.where(year_expr.between(filters.year_start, filters.year_end))
    elif filters.year_start:
        query = query.where(year_expr >= filters.year_start)
    elif filters.year_end:
        query = query.where(year_expr <= filters.year_end)

    if filters.status:
        query = query.where(Anime.status == filters.status)

    return session.scalars(query.limit(limit)).all()