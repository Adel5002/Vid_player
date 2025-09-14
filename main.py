import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from db.db import init_db
from endpoints.user import router as user_router
from endpoints.anime import router as anime_router
from endpoints.anime import add_anime_to_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    asyncio.create_task(add_anime_to_db())
    yield

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


if __name__ == "__main__":
    uvicorn.run(app)
