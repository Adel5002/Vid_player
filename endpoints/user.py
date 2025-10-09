from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from authorization.jwt_auth import get_current_user
from db.crud import update_profile_data
from db.db import get_session
from db import crud, models
from db.models import Profile, ProfileUpdate, ProfileRead

router = APIRouter()


@router.post("/create-user/", response_model=models.UserRead)
def create_user(user: models.UserCreate, session: Session = Depends(get_session)):
    return crud.create_user(session, user)


@router.get("/get-user/{user_id}", response_model=models.UserRead)
def get_user(
        user_id: int,
        session: Session = Depends(get_session),
        current_user = Depends(get_current_user)

):
    user = crud.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/update-user/{username}", response_model=models.UserRead)
def update_user(
        username: str,
        user: models.UserUpdate,
        session: Session = Depends(get_session),
        current_user = Depends(get_current_user)
):
    updated_user = crud.update_user_by_username(session, username, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/delete-user/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    deleted = crud.delete_user(session, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}

@router.patch('/update-profile/{profile_id}', response_model=ProfileRead)
async def update_profile(
        profile_data: ProfileUpdate,
        profile_id: int,
        session: Session = Depends(get_session)
) -> Profile:
    return update_profile_data(session, profile_data, profile_id)