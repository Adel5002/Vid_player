from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from db.db import get_session
from db import crud, models

router = APIRouter()


@router.post("/create-user/", response_model=models.UserRead)
def create_user(user: models.UserCreate, session: Session = Depends(get_session)):
    return crud.create_user(session, user)


@router.get("/get-user/{user_id}", response_model=models.UserRead)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = crud.get_user(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/update-user/{user_id}", response_model=models.UserRead)
def update_user(user_id: int, user: models.UserUpdate, session: Session = Depends(get_session)):
    updated_user = crud.update_user(session, user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/delete-user/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    deleted = crud.delete_user(session, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}
