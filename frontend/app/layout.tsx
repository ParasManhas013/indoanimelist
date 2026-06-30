import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { Analytics } from "@vercel/analytics/next";

export const metadata: Metadata = {
  title: "IndoAnimeList — India's Anime Leaderboard",
  description:
    "The definitive crowdsourced anime leaderboard for Indian fans. Powered by Bayesian ranking from real Indian viewer ratings.",
  keywords: ["anime", "leaderboard", "India", "ratings", "top anime", "IndoAnimeList"],
  openGraph: {
    title: "IndoAnimeList — India's Anime Leaderboard",
    description: "Top 50 anime ranked by Indian fans using Bayesian weighted scores.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main className="page-wrapper">
          {children}
        </main>
        <Analytics />
      </body>
    </html>
  );
}
