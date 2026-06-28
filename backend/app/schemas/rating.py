import uuid
from datetime import datetime
from pydantic import BaseModel, field_validator


class RatingCreate(BaseModel):
    anime_id: int
    score: float

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        if not 1.0 <= v <= 10.0:
            raise ValueError("Score must be between 1.0 and 10.0")
        return v


class RatingResponse(BaseModel):
    id: uuid.UUID
    anime_id: int
    score: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
