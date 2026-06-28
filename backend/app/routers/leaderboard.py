from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.anime import Anime
from app.schemas.anime import LeaderboardEntry
from app.services.cache_service import get_leaderboard_cache, set_leaderboard_cache
from app.config import settings

router = APIRouter(prefix="/api", tags=["leaderboard"])


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard(db: AsyncSession = Depends(get_db)):
    """
    Returns the Top 50 anime ranked by Bayesian Weighted Average.
    Results are cached in Redis for 60 seconds.
    Only anime with vote_count >= MIN_VOTES qualify.
    """
    # Try cache first
    cached = await get_leaderboard_cache()
    if cached:
        return cached

    # Query DB
    result = await db.execute(
        select(Anime)
        .where(Anime.vote_count >= settings.MIN_VOTES)
        .order_by(Anime.bayesian_avg.desc())
        .limit(50)
    )
    anime_list = result.scalars().all()

    # Build ranked response
    leaderboard = [
        {
            "rank": i + 1,
            "id": anime.id,
            "title": anime.title,
            "title_english": anime.title_english,
            "cover_image_url": anime.cover_image_url,
            "bayesian_avg": round(anime.bayesian_avg, 2),
            "vote_count": anime.vote_count,
        }
        for i, anime in enumerate(anime_list)
    ]

    # Cache and return
    await set_leaderboard_cache(leaderboard)
    return leaderboard
