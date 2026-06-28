from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from sqlalchemy.dialects.postgresql import array

from app.database import get_db
from app.models.anime import Anime
from app.models.rating import Rating
from app.schemas.anime import AnimeResponse, AnimeSearchResult
from app.services.auth_service import get_optional_user
from app.config import settings

router = APIRouter(prefix="/api/anime", tags=["anime"])


@router.get("/search", response_model=list[AnimeSearchResult])
async def search_anime(q: str = "", limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Fuzzy search the full 500-title catalog using pg_trgm."""
    if not q.strip():
        # Return latest/popular if no query
        result = await db.execute(
            select(Anime).order_by(Anime.vote_count.desc()).limit(limit)
        )
        anime_list = result.scalars().all()
    else:
        # Use pg_trgm similarity for fuzzy matching
        result = await db.execute(
            select(Anime)
            .where(
                or_(
                    func.similarity(Anime.title, q) > 0.1,
                    func.similarity(Anime.title_english, q) > 0.1,
                    Anime.title.ilike(f"%{q}%"),
                    Anime.title_english.ilike(f"%{q}%"),
                )
            )
            .order_by(
                func.greatest(
                    func.similarity(Anime.title, q),
                    func.coalesce(func.similarity(Anime.title_english, q), 0),
                ).desc()
            )
            .limit(limit)
        )
        anime_list = result.scalars().all()

    return [
        AnimeSearchResult(
            id=a.id,
            title=a.title,
            title_english=a.title_english,
            cover_image_url=a.cover_image_url,
            genres=a.genres,
            simple_avg=round(a.simple_avg, 2),
            bayesian_avg=round(a.bayesian_avg, 2),
            vote_count=a.vote_count,
            is_qualified=a.vote_count >= settings.MIN_VOTES,
        )
        for a in anime_list
    ]


@router.get("/{anime_id}", response_model=AnimeResponse)
async def get_anime(anime_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    """Get full anime details. If authenticated, also returns the user's own rating."""
    result = await db.execute(select(Anime).where(Anime.id == anime_id))
    anime = result.scalar_one_or_none()

    if not anime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found.")

    return anime
