"use client";

import Link from "next/link";
import Image from "next/image";
import { useRouter } from "next/navigation";
import type { LeaderboardEntry } from "@/lib/api";

interface Props {
  entries: LeaderboardEntry[];
}

function getRankClass(rank: number): string {
  if (rank === 1) return "rank-badge rank-1";
  if (rank === 2) return "rank-badge rank-2";
  if (rank === 3) return "rank-badge rank-3";
  return "rank-badge rank-default";
}

export function LeaderboardTable({ entries }: Props) {
  const router = useRouter();

  if (entries.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">📋</div>
        <p>No anime on the leaderboard yet. Be the first to rate!</p>
      </div>
    );
  }

  return (
    <div className="leaderboard-table">
      {entries.map((entry) => (
        <div
          key={entry.id}
          id={`leaderboard-row-${entry.id}`}
          className="leaderboard-row"
          onClick={() => router.push(`/anime/${entry.id}`)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === "Enter" && router.push(`/anime/${entry.id}`)}
        >
          {/* Rank */}
          <div className={getRankClass(entry.rank)}>
            {entry.rank <= 3 ? ["🥇", "🥈", "🥉"][entry.rank - 1] : entry.rank}
          </div>

          {/* Cover */}
          <div className="anime-cover-placeholder">
            {entry.cover_image_url ? (
              <Image
                src={entry.cover_image_url}
                alt={entry.title}
                width={56}
                height={72}
                className="anime-cover-sm"
                style={{ objectFit: "cover", borderRadius: "6px" }}
                unoptimized
              />
            ) : (
              <span>🎌</span>
            )}
          </div>

          {/* Info */}
          <div className="anime-info">
            <div className="anime-title-main">{entry.title}</div>
            {entry.title_english && entry.title_english !== entry.title && (
              <div className="anime-title-en">{entry.title_english}</div>
            )}
          </div>

          {/* Score */}
          <div className="score-badge">
            <div className="score-value">{entry.bayesian_avg.toFixed(2)}</div>
            <div className="score-label">Trusted</div>
          </div>

          {/* Votes */}
          <div className="vote-count">{entry.vote_count.toLocaleString()} votes</div>
        </div>
      ))}
    </div>
  );
}
