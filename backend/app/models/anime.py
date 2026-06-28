from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Text, func, Index
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Anime(Base):
    __tablename__ = "anime"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # MAL ID
    mal_id: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    title_english: Mapped[str | None] = mapped_column(String(512), nullable=True)
    synopsis: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_image_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    genres: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    simple_avg: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    bayesian_avg: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    vote_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        # GIN index for pg_trgm fuzzy search on title
        Index("ix_anime_title_trgm", "title", postgresql_using="gin",
              postgresql_ops={"title": "gin_trgm_ops"}),
        Index("ix_anime_title_english_trgm", "title_english", postgresql_using="gin",
              postgresql_ops={"title_english": "gin_trgm_ops"}),
    )
