from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.anime import Anime
from app.models.rating import Rating
from app.config import settings

router = APIRouter(prefix="/api/admin", tags=["admin"])


async def verify_admin_key(x_admin_key: str = Header(...)):
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid admin key.")


@router.get("/stats", dependencies=[Depends(verify_admin_key)])
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Admin endpoint: site-wide statistics."""
    total_users = await db.scalar(select(func.count(User.id)))
    verified_users = await db.scalar(select(func.count(User.id)).where(User.is_verified == True))
    total_ratings = await db.scalar(select(func.count(Rating.id)))
    total_anime = await db.scalar(select(func.count(Anime.id)))
    qualified_anime = await db.scalar(
        select(func.count(Anime.id)).where(Anime.vote_count >= settings.MIN_VOTES)
    )

    return {
        "total_users": total_users,
        "verified_users": verified_users,
        "total_ratings": total_ratings,
        "total_anime_in_catalog": total_anime,
        "anime_on_leaderboard": qualified_anime,
    }


@router.get("/config", dependencies=[Depends(verify_admin_key)])
async def get_config(db: AsyncSession = Depends(get_db)):
    """Admin endpoint: current ranking config."""
    global_mean = await db.scalar(
        select(func.avg(Rating.score)).where(Rating.user_id.is_not(None))
    )
    return {
        "min_votes_threshold": settings.MIN_VOTES,
        "leaderboard_cache_ttl_seconds": settings.LEADERBOARD_CACHE_TTL,
        "global_mean_rating": round(float(global_mean or 0), 4),
        "environment": settings.ENVIRONMENT,
    }
