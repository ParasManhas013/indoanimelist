import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.config import settings
from app.models.anime import Anime
from app.models.rating import Rating
from app.services.cache_service import invalidate_leaderboard_cache


async def upsert_rating(
    db: AsyncSession,
    user_id: uuid.UUID,
    anime_id: int,
    score: int,
) -> Rating:
    """Insert or update a user's rating for an anime."""
    # Check if rating already exists
    result = await db.execute(
        select(Rating).where(Rating.user_id == user_id, Rating.anime_id == anime_id)
    )
    rating = result.scalar_one_or_none()

    if rating:
        rating.score = score
    else:
        rating = Rating(user_id=user_id, anime_id=anime_id, score=score)
        db.add(rating)

    await db.commit()
    await db.refresh(rating)
    return rating


async def recalculate_stats(db: AsyncSession, anime_id: int) -> None:
    """
    Recalculate simple average, vote count, and Bayesian score for a given anime.
    Also invalidates the leaderboard Redis cache.

    Bayesian formula: (v * R + m * C) / (v + m)
    Where:
      v = vote count for this anime
      R = simple mean for this anime
      m = MIN_VOTES threshold
      C = global mean across all rated anime (dynamic)
    """
    # Get stats for this specific anime
    stats_result = await db.execute(
        select(
            func.count(Rating.id).label("vote_count"),
            func.avg(Rating.score).label("simple_avg"),
        ).where(Rating.anime_id == anime_id, Rating.user_id.is_not(None))
    )
    stats = stats_result.one()
    vote_count = stats.vote_count or 0
    simple_avg = float(stats.simple_avg or 0.0)

    # Get global mean C across all anime that have at least 1 vote
    global_result = await db.execute(
        select(func.avg(Rating.score)).where(Rating.user_id.is_not(None))
    )
    global_mean = float(global_result.scalar() or 0.0)

    m = settings.MIN_VOTES
    C = global_mean
    v = vote_count
    R = simple_avg

    # Bayesian weighted average
    bayesian_avg = (v * R + m * C) / (v + m) if (v + m) > 0 else 0.0

    # Update anime record
    result = await db.execute(select(Anime).where(Anime.id == anime_id))
    anime = result.scalar_one_or_none()
    if anime:
        anime.simple_avg = simple_avg
        anime.vote_count = vote_count
        anime.bayesian_avg = bayesian_avg
        await db.commit()

    # Invalidate leaderboard cache
    await invalidate_leaderboard_cache()
