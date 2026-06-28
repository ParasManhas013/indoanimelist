"""
IndoAnimeList — Jikan API Seeder
============================
One-time script to seed the database with the Top 500 anime from MyAnimeList
via the Jikan v4 API and store image URLs.

Usage:
    cd backend
    python -m scripts.seed
"""

import asyncio
import os
import sys

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.database import Base
from app.models.anime import Anime
from app.services.storage_service import upload_image

JIKAN_BASE = "https://api.jikan.moe/v4"
ANIME_PER_PAGE = 25
TOTAL_ANIME = 500
TOTAL_PAGES = TOTAL_ANIME // ANIME_PER_PAGE  # 20 pages
REQUEST_DELAY = 1.5  # seconds between requests (Jikan rate limit)


async def fetch_top_anime_page(client: httpx.AsyncClient, page: int) -> list[dict]:
    for attempt in range(3):
        try:
            response = await client.get(
                f"{JIKAN_BASE}/top/anime",
                params={"page": page, "limit": ANIME_PER_PAGE, "type": "tv"},
                timeout=15.0,
            )
            response.raise_for_status()
            return response.json().get("data", [])
        except Exception as e:
            print(f"  [WARN] Page {page} attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(3)
    return []


async def download_image(client: httpx.AsyncClient, url: str) -> bytes | None:
    try:
        response = await client.get(url, timeout=15.0)
        response.raise_for_status()
        return response.content
    except Exception:
        return None


async def seed():
    print("IndoAnimeList Seeder Starting...")
    print(f"Target: {TOTAL_ANIME} anime from Jikan API")
    print()

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Clear existing data
    print("Clearing existing anime and ratings data...")
    async with engine.begin() as conn:
        await conn.execute(text("DELETE FROM ratings"))
        await conn.execute(text("DELETE FROM anime"))
    print("Cleared.\n")

    all_anime_data = []

    async with httpx.AsyncClient() as client:
        for page in range(1, TOTAL_PAGES + 1):
            print(f"Fetching page {page}/{TOTAL_PAGES}...")
            anime_page = await fetch_top_anime_page(client, page)
            all_anime_data.extend(anime_page)
            print(f"  Got {len(anime_page)} anime (total: {len(all_anime_data)})")
            await asyncio.sleep(REQUEST_DELAY)

        print(f"\nFetched {len(all_anime_data)} anime. Loading into database...\n")

        async with SessionLocal() as db:
            for i, item in enumerate(all_anime_data, 1):
                mal_id = item.get("mal_id")
                title = item.get("title", "Unknown")
                title_english = item.get("title_english")
                synopsis = item.get("synopsis", "")
                genres = [g["name"] for g in item.get("genres", [])]
                image_url = item.get("images", {}).get("jpg", {}).get("large_image_url", "")

                print(f"[{i:3d}/{TOTAL_ANIME}] {title[:55]}")

                cover_url = image_url
                if image_url and settings.R2_ACCESS_KEY:
                    img_bytes = await download_image(client, image_url)
                    if img_bytes:
                        try:
                            cover_url = await upload_image(img_bytes, f"{mal_id}.jpg")
                            print(f"         Uploaded to R2")
                        except Exception as e:
                            print(f"         R2 failed, using MAL URL: {e}")
                else:
                    print(f"         Using MAL image URL")

                existing = await db.get(Anime, mal_id)
                if existing:
                    existing.title = title
                    existing.title_english = title_english
                    existing.synopsis = synopsis
                    existing.genres = genres
                    existing.cover_image_url = cover_url
                else:
                    anime = Anime(
                        id=mal_id,
                        mal_id=mal_id,
                        title=title,
                        title_english=title_english,
                        synopsis=synopsis,
                        cover_image_url=cover_url,
                        genres=genres,
                    )
                    db.add(anime)

                if i % 25 == 0:
                    await db.commit()
                    print(f"\n   Committed {i} records\n")

            await db.commit()

    print(f"\nSeeding complete! {len(all_anime_data)} anime loaded into the database.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
