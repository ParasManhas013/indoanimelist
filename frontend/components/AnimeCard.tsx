"use client";

import Link from "next/link";
import Image from "next/image";
import type { AnimeSearchResult } from "@/lib/api";

interface Props {
  anime: AnimeSearchResult;
}

export function AnimeCard({ anime }: Props) {
  const score = anime.is_qualified ? anime.bayesian_avg : anime.simple_avg;
  const scoreLabel = anime.is_qualified ? "Trusted Score" : "Avg Score";

  return (
    <Link href={`/anime/${anime.id}`} id={`anime-card-${anime.id}`}>
      <div className="anime-card">
        <div className="card-cover">
          {anime.cover_image_url ? (
            <Image
              src={anime.cover_image_url}
              alt={anime.title}
              fill
              style={{ objectFit: "cover" }}
              sizes="(max-width: 768px) 150px, 200px"
              unoptimized
            />
          ) : (
            <div
              style={{
                width: "100%",
                height: "100%",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "3rem",
                background: "var(--bg-secondary)",
              }}
            >
              🎌
            </div>
          )}
          {anime.is_qualified && (
            <span className="card-qualified-badge">⭐ Ranked</span>
          )}
        </div>

        <div className="card-body">
          <div className="card-title">{anime.title_english || anime.title}</div>

          {anime.genres.length > 0 && (
            <div className="card-genres">
              {anime.genres.slice(0, 2).map((g) => (
                <span key={g} className="genre-tag">{g}</span>
              ))}
            </div>
          )}

          <div className="card-footer">
            <div>
              <div className="card-score">
                {score > 0 ? score.toFixed(2) : "—"}
              </div>
              <div style={{ fontSize: "0.65rem", color: "var(--text-muted)" }}>{scoreLabel}</div>
            </div>
            <div className="card-votes">
              {anime.vote_count > 0 ? `${anime.vote_count} votes` : "No votes yet"}
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}
