from datetime import datetime
from pydantic import BaseModel


class AnimeResponse(BaseModel):
    id: int
    mal_id: int
    title: str
    title_english: str | None
    synopsis: str | None
    cover_image_url: str
    genres: list[str]
    simple_avg: float
    bayesian_avg: float
    vote_count: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class AnimeSearchResult(BaseModel):
    id: int
    title: str
    title_english: str | None
    cover_image_url: str
    genres: list[str]
    simple_avg: float
    bayesian_avg: float
    vote_count: int
    # Whether the title qualifies for the leaderboard
    is_qualified: bool

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    rank: int
    id: int
    title: str
    title_english: str | None
    cover_image_url: str
    bayesian_avg: float
    vote_count: int

    model_config = {"from_attributes": True}
