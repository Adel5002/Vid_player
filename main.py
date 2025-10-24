import os
import ngrok
from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from pytz import timezone
from loguru import logger
from dotenv import load_dotenv

from dramatiq_actors.db_update_actor import update_ongoings

load_dotenv()

from db.db import init_db, drop_db
from dramatiq_actors.db_fill_actor import fill_db
from dramatiq_actors.redis_key_availability import watch_expired_refresh_tokens
from endpoints.user import router as user_router
from endpoints.anime import router as anime_router
from endpoints.register import router as reg_router
from endpoints.watch_anime import router as watch_router
from redis_cache import cache

NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
NGROK_DOMAIN = os.getenv("NGROK_DOMAIN")
APPLICATION_PORT = 8000

scheduler = AsyncIOScheduler(timezone=timezone("Europe/Moscow"))
async def update_db():
    cache.delete('anime')
    fill_db.send()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    watch_expired_refresh_tokens.send()

    scheduler.add_job(update_db, "cron", hour=0, minute=0)
    scheduler.start()

    logger.info("Setting up Ngrok Endpoint")
    ngrok.set_auth_token(NGROK_AUTH_TOKEN)

    # Простой способ без указания proto
    public_url = ngrok.forward(
        addr=APPLICATION_PORT,
        domain=NGROK_DOMAIN,
        inspect=True,
    )

    logger.info(f"Ngrok tunnel created: {public_url}")
    yield
    logger.info("Tearing Down Ngrok Endpoint")
    ngrok.disconnect()

app = FastAPI(lifespan=lifespan, root_path="/api")

app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(anime_router, prefix="/anime", tags=["anime"])
app.include_router(reg_router, prefix="/reg", tags=["reg"])
app.include_router(watch_router, prefix="/watch-list", tags=["watch"])


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://potted-viscerally-kimora.ngrok-free.dev"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или ["*"] для всех origin
    allow_credentials=True,  # важно, если используешь куки
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: Сделать depends который будет проверять является ли юзер админом
@app.get('/drop-db/')
async def drop_db_endpoint():
    drop_db()
    init_db()
    cache.flushall()
    return {'status': 'ok'}


@app.get('/fill-db/')
async def fill_db_endpoint():
    fill_db.send()
    return {'status': 'ok'}

@app.get('/update-db/')
async def update_db():
    update_ongoings.send()
    return {'status': 'ok'}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=APPLICATION_PORT)

