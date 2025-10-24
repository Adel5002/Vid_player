import base64
import json
import re
from typing import Optional, Dict, Any
from fastapi import HTTPException
from numpy.random.mtrand import Sequence
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select, desc, col, or_
from fastapi.responses import JSONResponse

from authorization.jwt_auth import get_password_hash
from .models import (
    User, UserCreate, UserUpdate,
    Anime, AnimeCreate, AnimePoster, AnimePosterCreate,
    Genre, GenreCreate, AnimeGenreLink,
    AnimeInfo, AnimeInfoCreate, AnimeRead, Profile, ProfileCreate, WatchAnimeCreate, WatchAnime, WatchAnimeUpdate
)


# ------------------ User ------------------
def create_user(session: Session, user_data: UserCreate) -> User:
    password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=password
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user(session: Session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)


def get_user_by_username(session: Session, username: str) -> Optional[User]:
    return session.scalar(select(User).where(User.username == username))


def update_user_by_id(session: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    user = session.get(User, user_id)
    if not user:
        return None

    password = get_password_hash(user_data.password)
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "password":
            setattr(user, "password", password)
        else:
            setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def update_user_by_username(session: Session, username: str, user_data: UserUpdate) -> Optional[User]:
    user = session.scalar(select(User).where(User.username == username))
    if not user:
        return None

    update_data = user_data.model_dump(exclude_unset=True)

    if user_data.password:
        password = get_password_hash(user_data.password)
    else:
        password = None

    for key, value in update_data.items():
        if key == "password":
            setattr(user, "password", password)
        else:
            setattr(user, key, value)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, user_id: int) -> dict[str, str]:
    user = session.get(User, user_id)
    if not user:
        return {'success': 'fail'}
    session.delete(user)
    session.commit()
    return {'success': 'ok'}


# ------------------ Profile ------------------
def read_profile(session: Session, profile_id: int) -> Optional[Profile]:
    profile = session.get(Profile, profile_id)

    if not profile:
        raise HTTPException(status_code=404, detail="Profile with this id does not exists")

    return profile


# ------------------ WatchAnime ------------------
def create_watch_anime(session: Session, watch_anime_data: WatchAnimeCreate) -> Optional[WatchAnime]:
    profile_exists = session.get(Profile, watch_anime_data.profile_id)
    anime_exists = session.get(Anime, watch_anime_data.anime_id)

    if not profile_exists:
        raise HTTPException(status_code=404, detail="Profile with this id does not exists")
    elif not anime_exists:
        raise HTTPException(status_code=404, detail="Profile with this id does not exists")

    watch_anime = WatchAnime(
        **watch_anime_data.model_dump()
    )
    session.add(watch_anime)
    session.commit()
    session.refresh(watch_anime)

    return watch_anime

def update_watch_anime(session: Session, watch_anime_id: int, watch_anime_data: WatchAnimeUpdate) -> Optional[WatchAnime]:
    watch_anime_exists = session.get(WatchAnime, watch_anime_id)

    if not watch_anime_exists:
        raise HTTPException(status_code=404, detail="Watch anime does not exists")

    watch_anime_exists.sqlmodel_update(watch_anime_data.model_dump(exclude_unset=True))
    session.add(watch_anime_exists)
    session.commit()
    session.refresh(watch_anime_exists)

    return watch_anime_exists

def read_watch_anime(session: Session, watch_anime_id: int) -> Optional[WatchAnime]:
    watch_anime = session.get(WatchAnime, watch_anime_id)

    if not watch_anime:
        raise HTTPException(status_code=404, detail="Watch anime does not exists")

    return watch_anime

def read_watch_anime_by_profile_id(session: Session, profile_id: int, anime_id: int) -> Optional[WatchAnime]:
    watch_anime = session.scalar(
        select(WatchAnime)
        .where(WatchAnime.profile_id == profile_id)
        .where(WatchAnime.anime_id == anime_id)
    )

    if not watch_anime:
        raise HTTPException(status_code=404, detail="Not Found")

    return watch_anime

def delete_watch_anime(session: Session, watch_anime_id: int) -> JSONResponse:
    watch_anime = session.get(WatchAnime, watch_anime_id)

    if not watch_anime:
        raise HTTPException(status_code=404, detail="Watch list id does not exists")

    session.delete(watch_anime)
    session.commit()
    return JSONResponse({"status": "ok"})

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


def read_anime(session: Session, anime_id: int) -> Optional[Anime]:
    anime = session.get(Anime, anime_id)
    if not anime:
        raise HTTPException(404, "Anime not found")
    return anime


def get_anime_by_name(session: Session, name: str) -> Sequence[dict]:
    animes = session.scalars(
        select(Anime)
        .filter(
            or_(
                col(Anime.name).icontains(name),
                col(Anime.russian).icontains(name)
            )
        )
        .options(
            selectinload(Anime.info),
            selectinload(Anime.poster),
        )
    ).all()

    result = []
    for item in animes:
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

    if len(result) == 0:
        raise HTTPException(status_code=404, detail="Anime not found")

    return result

from sqlalchemy import case, select, desc, func, cast, Integer, and_, asc, Numeric
from sqlalchemy.orm import selectinload, contains_eager
import datetime
from typing import Sequence

def get_anime_bulk(session: Session) -> Sequence[Anime]:
    # Добавить сортировку по сезону
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
        .join(AnimeInfo)
        .where(
            Anime.season.contains(str(current_year)),
            AnimeInfo.kodik_player_url != "none",
            Anime.score > 0
        )
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

def get_anime_by_shikimori_id(shikimori_id: int, session: Session) -> Optional[dict]:
    anime = session.scalar(select(Anime).where(Anime.shikimori_id == shikimori_id))
    if not anime:
        return None

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
            created_at=anime.created_at,
            updated_at=anime.updated_at,
        ).model_dump()

    return anime

from fastapi import HTTPException
from sqlmodel import Session, select
from db.models import Anime, AnimeInfo


def update_anime(session: Session, anime_id: int, anime_data):
    # Пробуем найти аниме по ID или Shikimori ID
    anime = session.scalar(
        select(Anime).where(
            or_(Anime.id == anime_id, Anime.shikimori_id == anime_id)
        )
    )
    if not anime:
        raise HTTPException(404, "Anime not found")

    # --- Обновляем основные поля (кроме info) ---
    anime.sqlmodel_update(
        anime_data.model_dump(exclude_unset=True, exclude={"info"})
    )

    # --- Обновляем info ---
    if anime_data.info:
        # если в info передан shikimori_id — используем его
        info_query = (
            select(AnimeInfo)
            .where(
                or_(AnimeInfo.shikimori_id == anime_data.shikimori_id, AnimeInfo.anime_id == anime.id)
            )
        )

        anime_info = session.scalar(info_query)

        if anime_info:
            anime_info.sqlmodel_update(
                anime_data.info.model_dump(exclude_unset=True)
            )
            session.add(anime_info)
        else:
            new_info = AnimeInfo(
                anime_id=anime.id,
                **anime_data.info.model_dump(exclude_unset=True),
            )
            session.add(new_info)

    session.add(anime)
    session.commit()
    session.refresh(anime)

    return anime


def get_all_possible_anime(session: Session) -> Sequence[Anime]:
    return session.scalars(select(Anime)).all()

def delete_anime(session: Session, anime_id: int) -> dict[str, str]:
    anime = session.get(Anime, anime_id)
    if not anime:
        return {'success': 'fail'}
    session.delete(anime)
    session.commit()
    return {'success': 'ok'}


def encode_page(data: Dict[str, Any]) -> str:
    """Кодирует словарь в base64 (URL-safe)."""
    raw = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode()
    return base64.urlsafe_b64encode(raw).decode()


def decode_page(token: str) -> Dict[str, Any]:
    """Декодирует base64 токен в словарь (безопасно)."""
    try:
        raw = base64.urlsafe_b64decode(token.encode())
        return json.loads(raw.decode())
    except Exception:
        return {}



def popular_anime_get(
    session: Session,
    limit: int,
    next_page: Optional[str] = None,
    prev_page: Optional[str] = None,
):
    """
    Двунаправленная пагинация по (season_year DESC, score DESC)
    с base64-курсорами next_page / prev_page.

    Возвращает:
      {
        "items": [...],
        "next_page": "<base64>|None",
        "prev_page": "<base64>|None",
        "has_next": bool,
        "has_prev": bool
      }
    """

    # безопасные выражения:
    # 1) год из season: CAST(NULLIF(regexp_replace(...), '' ) AS INTEGER)
    season_year_expr = cast(
        func.nullif(func.regexp_replace(
            # season вида 'fall_2023' → '2023'
            # всё, что не цифра, убираем
            # если цифр нет → '' → NULL
            # затем CAST(NULL AS INTEGER) безопасно
            # важно: это одно выражение переиспользуем везде
            # чтобы не дублировать и не ошибиться
            # Anime.season можно заменить на нужную колонку
            # например models.Anime.season
            # здесь предполагаю модель Anime уже импортирована
            # см. импорт выше
            # ↓↓↓
            # Anime.season
            # ↑↑↑
            Anime.season,
            '[^0-9]', '', 'g'
        ), ''),
        Integer
    )

    # базовые фильтры: валидные season + не "anons" и год реально извлечён
    base = select(Anime).where(
        Anime.season.is_not(None),
        ~Anime.season.in_(["?", "unknown", "", "None"]),
        Anime.status != "anons",
        season_year_expr.is_not(None),
        Anime.score > 6
    )

    # определяем направление и раскодируем токен
    direction = "next" if next_page else ("prev" if prev_page else None)
    page_data = decode_page(next_page or prev_page) if (next_page or prev_page) else None

    # применяем курсор-фильтр
    if page_data:
        # выдернем год из season, например "spring_2025" -> 2025
        m = re.search(r"[0-9]+", page_data.get("season", "") or "")
        season_year_val = int(m.group()) if m else 0

        # score из токена; если был строкой — ОК, приводим к float для корректного сравнения как числа
        score_val = page_data.get("score", 0)
        try:
            score_val = float(score_val)
        except Exception:
            score_val = 0.0

        if direction == "next":
            # всё, что идёт ПОСЛЕ текущей позиции в порядке (year DESC, score DESC):
            #   year < Y  OR (year = Y AND score < S)
            base = base.where(
                or_(
                    season_year_expr < season_year_val,
                    and_(season_year_expr == season_year_val, Anime.score < score_val),
                )
            )
        else:
            # всё, что идёт ДО текущей позиции (для prev) — зеркально:
            #   year > Y  OR (year = Y AND score > S)
            base = base.where(
                or_(
                    season_year_expr > season_year_val,
                    and_(season_year_expr == season_year_val, Anime.score > score_val),
                )
            )

    # сортировка: для next — DESC, для prev — ASC (идём в обратную сторону)
    order = desc if direction != "prev" else asc
    base = base.order_by(
        order(season_year_expr),
        order(Anime.score)
    ).limit(limit + 1)

    rows = session.scalars(base).all()

    # если шли назад — разворачиваем, чтобы на фронт отдать в «обычном» порядке
    if direction == "prev":
        rows = list(reversed(rows))

    # первые limit — это текущая страница
    items = [
        AnimeRead(**r.model_dump(), poster=r.poster)
        for r in rows[:limit]
    ]

    # флаги и курсоры на обе стороны
    has_next = has_prev = False

    if direction == "next":
        has_next = len(rows) > limit
        has_prev = True if (next_page or prev_page) else False  # если уже листали — назад есть
    elif direction == "prev":
        has_prev = len(rows) > limit
        has_next = True  # если листали назад, вперёд точно есть
    else:
        # первая страница без курсоров
        has_next = len(rows) > limit
        has_prev = False

    # упаковываем курсоры
    next_page_token = prev_page_token = None
    if items:
        first, last = items[0], items[-1]
        next_page_token = encode_page({"season": last.season, "score": last.score})
        prev_page_token = encode_page({"season": first.season, "score": first.score})

    return {
        "items": items,
        "next_page": (next_page_token if has_next else None),
        "prev_page": (prev_page_token if has_prev else None),
        "has_next": has_next,
        "has_prev": has_prev,
    }


# ------------------ Anime Info ------------------
def create_anime_info(session: Session, info_data: AnimeInfoCreate) -> AnimeInfo:
    # Проверяем, есть ли уже запись для этого anime_id
    anime_info = session.scalars(select(AnimeInfo).where(AnimeInfo.anime_id == info_data.anime_id)).first()

    if not anime_info:
        anime_info = AnimeInfo(**info_data.model_dump(exclude={"genres"}))
        session.add(anime_info)
        session.commit()
        session.refresh(anime_info)

    # Обрабатываем жанры
    if info_data.genres:
        for g in info_data.genres:
            # Проверяем, есть ли такой жанр в таблице Genre
            genre = session.scalars(select(Genre).where(Genre.name == g.name)).first()
            if not genre:
                genre = Genre(name=g.name, russian=g.russian)
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

    for field, value in info_data.model_dump(exclude_unset=True).items():
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


def delete_anime_info(session: Session, info_id: int) -> dict[str, str]:
    info = session.get(AnimeInfo, info_id)
    if not info:
        return {'success': 'fail'}
    session.delete(info)
    session.commit()
    return {'success': 'ok'}


def get_all_anime_info(session: Session) -> Sequence[AnimeInfo]:
    return session.scalars(select(AnimeInfo)).all()


# ------------------ Genre ------------------
def create_genre(session: Session, genre_data: GenreCreate) -> Optional[Genre]:
    genre_exists = session.scalar(select(Genre).where(Genre.name == genre_data.name))

    if genre_exists:
        return None

    genre = Genre(name=genre_data.name)
    session.add(genre)
    session.commit()
    session.refresh(genre)
    return genre

def read_genre(session: Session, genre_id: int) -> Optional[Genre]:
    return session.get(Genre, genre_id)

def get_all_genres(session: Session) -> Sequence[Genre]:
    return session.scalars(select(Genre)).all()


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
