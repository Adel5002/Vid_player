from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db.crud import create_watch_anime, update_watch_anime, read_watch_anime, read_watch_anime_by_profile_id
from db.db import get_session
from db.models import WatchAnime, WatchAnimeCreate, WatchAnimeUpdate, WatchAnimeRead

router = APIRouter()

@router.post("/create-watch-anime/", response_model=WatchAnimeRead)
async def watch_anime_create(watch_anime_data: WatchAnimeCreate, session: Session = Depends(get_session)) -> WatchAnime:
    get_watch = session.scalar(select(WatchAnime)
                               .where(WatchAnime.profile_id == watch_anime_data.profile_id)
                               .where(WatchAnime.anime_id == watch_anime_data.anime_id))
    if get_watch:
        raise HTTPException(status_code=409, detail="Anime already added to the watch list,"
                                                    " update it instead of creating it again")

    return create_watch_anime(session, watch_anime_data)

@router.patch("/update-watch-anime/{watch_anime_id}", response_model=WatchAnimeRead)
async def watch_anime_create(
        watch_anime_id: int,
        watch_anime_data: WatchAnimeUpdate,
        session: Session = Depends(get_session)
) -> WatchAnime:
    return update_watch_anime(session, watch_anime_id, watch_anime_data)

@router.get("/get-watch-anime/{watch_anime_id}", response_model=WatchAnimeRead)
async def watch_anime_get(watch_anime_id: int, session: Session = Depends(get_session)) -> WatchAnime:
    return read_watch_anime(session, watch_anime_id)

@router.get("/get-watch-anime-by-profile-id/{profile_id}/{anime_id}", response_model=WatchAnimeRead)
async def watch_anime_get_by_profile_id(profile_id: int, anime_id: int, session: Session = Depends(get_session)) -> WatchAnime:
    return read_watch_anime_by_profile_id(session, profile_id, anime_id)