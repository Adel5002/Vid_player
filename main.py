import asyncio
from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from pytz import timezone

from db.db import init_db, drop_db
from dramatiq_actors.db_fill_actor import fill_db
from endpoints.user import router as user_router
from endpoints.anime import router as anime_router
from redis_cache import cache

scheduler = AsyncIOScheduler(timezone=timezone("Europe/Moscow"))
async def update_db():
    cache.delete('anime')
    fill_db.send()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    scheduler.add_job(update_db, "cron", hour=0, minute=0)
    scheduler.start()
    yield
    # cache.flushall()

app = FastAPI(lifespan=lifespan)

app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(anime_router, prefix="/anime", tags=["anime"])


origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # или ["*"] для всех origin
    allow_credentials=True,  # важно, если используешь куки
    allow_methods=["*"],
    allow_headers=["*"],
)

# TODO: Исправить ошибку - При сбрасывании бд круд отвечающий за глав страницу выдает ошибку из-за логики сортировки
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

