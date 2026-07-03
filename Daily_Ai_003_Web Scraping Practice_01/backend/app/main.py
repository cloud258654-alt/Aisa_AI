from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.articles import router as articles_router
from app.api.health import router as health_router
from app.api.images import router as images_router
from app.api.popular import router as popular_router
from app.api.search import router as search_router
from app.api.statistics import router as statistics_router
from app.database.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="PTT Joke Meme PWA", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api")
app.include_router(statistics_router, prefix="/api")
app.include_router(articles_router, prefix="/api")
app.include_router(images_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(popular_router, prefix="/api")
