from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.routers import auth, leaderboard, anime, ratings, admin

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="IndoAnimeList API",
    description="Backend for India's Anime Leaderboard",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(leaderboard.router)
app.include_router(anime.router)
app.include_router(ratings.router)
app.include_router(admin.router)


@app.get("/api/health", tags=["health"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "env": settings.ENVIRONMENT}


@app.on_event("startup")
async def startup_event():
    print(f"🚀 {settings.APP_NAME} API started in [{settings.ENVIRONMENT}] mode")
