from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.anime import Anime
from app.models.rating import Rating
from app.schemas.rating import RatingCreate, RatingResponse
from app.services.auth_service import get_current_user
from app.services import rating_service

router = APIRouter(prefix="/api", tags=["ratings"])


@router.post("/rate", response_model=RatingResponse, status_code=status.HTTP_200_OK)
async def submit_rating(
    payload: RatingCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit or update a rating (1–10) for an anime.
    JWT-protected. Unauthenticated requests return 401.
    Bayesian recalculation runs in the background after the response is sent.
    """
    current_user = await get_current_user(db, request.cookies.get("access_token"))

    # Verify anime exists
    result = await db.execute(select(Anime).where(Anime.id == payload.anime_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found.")

    # Upsert the rating
    rating = await rating_service.upsert_rating(db, current_user.id, payload.anime_id, payload.score)

    # Recalculate Bayesian stats in background (non-blocking).
    # recalculate_stats opens its own DB session — the request session is
    # already closed by the time BackgroundTasks execute.
    background_tasks.add_task(rating_service.recalculate_stats, payload.anime_id)

    return rating


@router.get("/rate/{anime_id}", response_model=RatingResponse | None)
async def get_my_rating(anime_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    """Get the current user's rating for a specific anime. Returns null if not rated."""
    current_user = await get_current_user(db, request.cookies.get("access_token"))

    result = await db.execute(
        select(Rating).where(Rating.user_id == current_user.id, Rating.anime_id == anime_id)
    )
    return result.scalar_one_or_none()
