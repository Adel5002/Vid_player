import json

from sqlmodel import Session
from fastapi import Request, HTTPException

from db.db import engine
from db.models import User


def is_user_admin(request: Request) -> None:
    with Session(engine) as session:
        user_id = json.loads(request.cookies.get("user")).get("id")
        user = session.get(User, user_id)

        if not user.is_admin:
            print("User is not admin")
            raise HTTPException(status_code=403, detail="User is not admin")