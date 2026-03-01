from app.api.auth import router as auth_router
from app.api.decks import router as decks_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.reviews import router as reviews_router
from app.api.words import router as words_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="EbbVocab API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(decks_router)
app.include_router(words_router)
app.include_router(reviews_router)
