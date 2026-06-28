import { fetchLeaderboard } from "@/lib/api";
import { LeaderboardTable } from "@/components/LeaderboardTable";

export const revalidate = 60; // ISR: revalidate every 60 seconds

export default async function HomePage() {
  const leaderboard = await fetchLeaderboard().catch(() => []);

  return (
    <div className="container">
      {/* Hero */}
      <section className="hero">
        <div className="hero-badge">🇮🇳 India&apos;s Anime Leaderboard</div>
        <h1>
          The <span className="highlight">Top 50</span> Anime<br />
          Rated by India
        </h1>
        <p className="hero-sub">
          Crowdsourced ratings from Indian fans, ranked using the{" "}
          <strong>Bayesian Weighted Average</strong> — the same algorithm used by IMDb.
        </p>
        <div className="hero-stats">
          <div className="hero-stat">
            <div className="hero-stat-value">500</div>
            <div className="hero-stat-label">Anime in Catalog</div>
          </div>
          <div className="hero-stat">
            <div className="hero-stat-value">{leaderboard.length}</div>
            <div className="hero-stat-label">On Leaderboard</div>
          </div>
          <div className="hero-stat">
            <div className="hero-stat-value">25+</div>
            <div className="hero-stat-label">Votes to Qualify</div>
          </div>
        </div>
      </section>

      {/* Leaderboard */}
      <section className="leaderboard-section">
        <div className="section-header">
          <h2 className="section-title">
            🏆 Top {leaderboard.length} Leaderboard
          </h2>
          <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
            Updated in real-time
          </span>
        </div>
        <LeaderboardTable entries={leaderboard} />
      </section>
    </div>
  );
}
