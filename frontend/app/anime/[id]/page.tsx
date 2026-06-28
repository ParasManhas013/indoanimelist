import { fetchAnime, fetchMe, fetchMyRating } from "@/lib/api";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import { RatingWidget } from "@/components/RatingWidget";
import type { Metadata } from "next";

interface Props {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const anime = await fetchAnime(Number(id)).catch(() => null);
  if (!anime) return { title: "Anime Not Found — IndoAnimeList" };
  return {
    title: `${anime.title_english || anime.title} — IndoAnimeList`,
    description: anime.synopsis?.slice(0, 160) ?? "View ratings and details on IndoAnimeList.",
  };
}

export default async function AnimeDetailPage({ params }: Props) {
  const { id } = await params;
  const animeId = Number(id);
  const [anime, user] = await Promise.all([
    fetchAnime(animeId).catch(() => null),
    fetchMe(),
  ]);

  if (!anime) notFound();

  const userRating = user ? await fetchMyRating(animeId).catch(() => null) : null;
  const isQualified = anime.vote_count >= 25;

  return (
    <div className="container anime-detail">
      <Link href="/search" className="detail-back">
        ← Back to Catalog
      </Link>

      <div className="detail-grid">
        {/* Cover */}
        <div>
          {anime.cover_image_url ? (
            <Image
              src={anime.cover_image_url}
              alt={anime.title}
              width={280}
              height={420}
              className="detail-cover"
              style={{ width: "100%", height: "auto" }}
              unoptimized
            />
          ) : (
            <div className="detail-cover-placeholder">🎌</div>
          )}
        </div>

        {/* Details */}
        <div className="detail-content">
          <h1>{anime.title}</h1>
          {anime.title_english && anime.title_english !== anime.title && (
            <p className="detail-en-title">{anime.title_english}</p>
          )}

          <div className="detail-meta">
            <div className="detail-stat">
              <div className="detail-stat-value">
                {isQualified
                  ? anime.bayesian_avg.toFixed(2)
                  : anime.simple_avg > 0
                  ? anime.simple_avg.toFixed(2)
                  : "—"}
              </div>
              <div className="detail-stat-label">
                {isQualified ? "Trusted Score" : "Simple Avg"}
              </div>
            </div>
            <div className="detail-stat">
              <div className="detail-stat-value">{anime.vote_count.toLocaleString()}</div>
              <div className="detail-stat-label">Indian Votes</div>
            </div>
            {isQualified && (
              <div className="detail-stat">
                <div className="detail-stat-value" style={{ color: "var(--green-accent)" }}>
                  ✓
                </div>
                <div className="detail-stat-label">On Leaderboard</div>
              </div>
            )}
          </div>

          {anime.genres.length > 0 && (
            <div className="detail-genres">
              {anime.genres.map((g) => (
                <span key={g} className="genre-tag">{g}</span>
              ))}
            </div>
          )}

          {anime.synopsis && (
            <p className="detail-synopsis">{anime.synopsis}</p>
          )}

          {/* Rating Widget */}
          <RatingWidget
            animeId={animeId}
            user={user}
            initialRating={userRating?.score ?? null}
          />
        </div>
      </div>
    </div>
  );
}
