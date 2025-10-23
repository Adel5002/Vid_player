import asyncio
import os
from datetime import timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from dotenv import load_dotenv

load_dotenv()

from authorization.jwt_auth import authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, \
    REFRESH_TOKEN_EXPIRE_DAYS, create_refresh_token, REFRESH_SECRET_KEY, ALGORITHM, ACCESS_SECRET_KEY, \
    get_password_hash, create_email_verification_token, EMAIL_SECRET_KEY, EMAIL_TOKEN_EXPIRE_HOURS
from db.db import get_session
from db.models import UserCreate, User, Profile
from redis_cache import cache

from utils.fastapi_verification_mail import send_verification_email

router = APIRouter()

@router.get("/check-access-token-activity/")
async def check_access_token_activity(token: str) -> JSONResponse:
    try:
        jwt.decode(token, ACCESS_SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Access token expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Access token invalid.")

    return JSONResponse({
        "status": "active"
    })

@router.post("/access-token")
async def login_for_access_token(refresh_token: str) -> JSONResponse:
    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

    stored = cache.get(f"refresh:{username}").decode('utf-8')
    print(stored)
    if not stored or stored != refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found or revoked.")

    # Создаём новый access токен
    access_payload = {"sub": username}
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=access_payload, expires_delta=access_token_expires
    )

    # Обновляем refresh токен
    new_refresh_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    new_refresh_token = create_refresh_token(
        data=access_payload, expires_delta=new_refresh_expires
    )
    cache.setex(f"refresh:{username}", new_refresh_expires, new_refresh_token)

    return JSONResponse({
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    })


ATTEMPT_LIMIT = 5       # макс. попыток
WINDOW = 60             # окно 60 с
BLOCK_TIME = 60 * 5     # блок на 5 минут

@router.post("/refresh-token")
async def get_new_refresh_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
) -> JSONResponse:
    ip = request.client.host
    key = f"login_attempts:{ip}"

    # Проверяем, не заблокирован ли IP
    if cache.get(f"blocked:{ip}"):
        raise HTTPException(
            status_code=429,
            detail="Слишком много попыток входа. Попробуйте позже."
        )

    # Увеличиваем счётчик
    attempts = cache.incr(key)
    if attempts == 1:
        cache.expire(key, WINDOW)

    # Если превышен лимит — баним
    if attempts > ATTEMPT_LIMIT:
        cache.setex(f"blocked:{ip}", BLOCK_TIME, "1")
        raise HTTPException(
            status_code=429,
            detail="Слишком много попыток входа. Попробуйте позже."
        )

    # Проверяем пользователя
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        # искусственная задержка при ошибке
        if attempts > 2:
            await asyncio.sleep(2 * (attempts - 2))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not verified yet",
        )

    # Успешный вход — сбрасываем счётчик
    cache.delete(key)

    payload = {"sub": user.username}
    access_token = create_access_token(
        data=payload, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data=payload, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    cache.setex(
        f"refresh:{user.username}",
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        refresh_token
    )

    user.disabled = False
    session.add(user)
    session.commit()
    session.refresh(user)

    return JSONResponse({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    })


@router.post("/register")
async def register_user(user_data: UserCreate, session: Session = Depends(get_session)) -> JSONResponse:
    existing_email = session.scalar(select(User).where(User.email == user_data.email))
    existing_username = session.scalar(select(User).where(User.username == user_data.username))

    if existing_email:
        raise HTTPException(status_code=400, detail="This email already in use")
    elif existing_username:
        raise HTTPException(status_code=400, detail="This username already in use")

    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        is_verified=False
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    new_profile = Profile(
        user_id=new_user.id
    )

    session.add(new_profile)
    session.commit()
    session.refresh(new_profile)

    # Генерация токена
    token = create_email_verification_token(new_user.email)
    verification_link = f"{os.getenv('MAIN_URL')}/reg/verify-email?token={token}"

    cache.setex(f"email_token:{new_user.username}", timedelta(hours=EMAIL_TOKEN_EXPIRE_HOURS), token)

    # TODO: на проде заменить на new_user.email
    # await send_verification_email(os.getenv('TEST_EMAIL'), verification_link)

    print(verification_link)
    return JSONResponse({"message": f"User created. Check your email for verification."})

from fastapi.responses import RedirectResponse

FRONTEND_URL = "http://localhost:5173"

@router.get("/verify-email")
async def verify_email(token: str, session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, EMAIL_SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise ValueError("No subject in token")
    except (jwt.PyJWTError, ValueError):
        return RedirectResponse(
            url=f"{FRONTEND_URL}/verify-email?status=error&reason=invalid_token",
            status_code=302
        )

    user = session.scalar(select(User).where(User.email == email))
    if not user:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/verify-email?status=error&reason=user_not_found",
            status_code=302
        )

    cached_email_token = cache.get(f"email_token:{user.username}")
    if not cached_email_token:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/verify-email?status=error&reason=expired_or_used",
            status_code=302
        )

    # Всё ок — подтверждаем почту
    user.is_verified = True
    session.add(user)
    session.commit()
    cache.delete(f"email_token:{user.username}")

    return RedirectResponse(
        url=f"{FRONTEND_URL}/verify-email?status=success",
        status_code=302
    )

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("user")
    return {"message": "Logged out"}
