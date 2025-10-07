import os
from datetime import timedelta, datetime, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel

from dotenv import load_dotenv
from sqlmodel import Session, select

from db.db import engine
from db.models import User

load_dotenv()

ACCESS_SECRET_KEY = os.getenv('JWT_ACCESS_SECRET_KEY')
REFRESH_SECRET_KEY = os.getenv('JWT_REFRESH_SECRET_KEY')
EMAIL_SECRET_KEY = os.getenv('JWT_EMAIL_SECRET_KEY')
ALGORITHM = os.getenv('JWT_ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES'))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS'))
EMAIL_TOKEN_EXPIRE_HOURS = int(os.getenv('JWT_EMAIL_TOKEN_EXPIRE_HOURS'))

class TokenData(BaseModel):
    username: str | None = None


password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)


def get_user(username: str, session: Session):
    user_exists = session.scalar(select(User).where(User.username == username))

    if not user_exists:
        return None
    return user_exists

def authenticate_user(username: str, password: str, session: Session):
    user = get_user(username, session)
    print(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ACCESS_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    with Session(engine) as session:
        user = get_user(token_data.username, session)
        if user is None or user.disabled:
            raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User does not exists or was disabled",
        headers={"WWW-Authenticate": "Bearer"},
    )
        return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def create_email_verification_token(email: str, expires_delta: timedelta | None = None):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=EMAIL_TOKEN_EXPIRE_HOURS)

    payload = {"sub": email, "exp": expire}
    token = jwt.encode(payload, EMAIL_SECRET_KEY, algorithm=ALGORITHM)
    return token