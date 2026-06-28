const IS_SERVER = typeof window === "undefined";
// Use proxy (empty string) on client to avoid CORS and cookie domain issues.
// Use absolute URL on server because relative fetch fails in Server Components.
const API_BASE = IS_SERVER ? (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000") : "";

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const fetchOptions: RequestInit = {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  };

  if (IS_SERVER) {
    const { cookies } = await import("next/headers");
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;
    if (token) {
      fetchOptions.headers = {
        ...fetchOptions.headers,
        Cookie: `access_token=${token}`,
      };
    }
  }

  const res = await fetch(`${API_BASE}${path}`, fetchOptions);

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

// ── Leaderboard ───────────────────────────────────────────────────────────────

export interface LeaderboardEntry {
  rank: number;
  id: number;
  title: string;
  title_english: string | null;
  cover_image_url: string;
  bayesian_avg: number;
  vote_count: number;
}

export async function fetchLeaderboard(): Promise<LeaderboardEntry[]> {
  return apiFetch<LeaderboardEntry[]>("/api/leaderboard");
}

// ── Anime ─────────────────────────────────────────────────────────────────────

export interface AnimeDetail {
  id: number;
  mal_id: number;
  title: string;
  title_english: string | null;
  synopsis: string | null;
  cover_image_url: string;
  genres: string[];
  simple_avg: number;
  bayesian_avg: number;
  vote_count: number;
}

export interface AnimeSearchResult {
  id: number;
  title: string;
  title_english: string | null;
  cover_image_url: string;
  genres: string[];
  simple_avg: number;
  bayesian_avg: number;
  vote_count: number;
  is_qualified: boolean;
}

export async function fetchAnime(id: number): Promise<AnimeDetail> {
  return apiFetch<AnimeDetail>(`/api/anime/${id}`);
}

export async function searchAnime(q: string): Promise<AnimeSearchResult[]> {
  return apiFetch<AnimeSearchResult[]>(`/api/anime/search?q=${encodeURIComponent(q)}`);
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  is_verified: boolean;
  created_at: string;
}

export async function register(email: string, password: string): Promise<{ message: string }> {
  return apiFetch("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function login(email: string, password: string): Promise<{ message: string }> {
  return apiFetch("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function logout(): Promise<void> {
  await apiFetch("/api/auth/logout", { method: "POST" });
}

export async function fetchMe(): Promise<User | null> {
  try {
    return await apiFetch<User>("/api/auth/me");
  } catch {
    return null;
  }
}

// ── Ratings ───────────────────────────────────────────────────────────────────

export interface Rating {
  id: string;
  anime_id: number;
  score: number;
  created_at: string;
  updated_at: string;
}

export async function submitRating(anime_id: number, score: number): Promise<Rating> {
  return apiFetch<Rating>("/api/rate", {
    method: "POST",
    body: JSON.stringify({ anime_id, score }),
  });
}

export async function fetchMyRating(anime_id: number): Promise<Rating | null> {
  try {
    return await apiFetch<Rating>(`/api/rate/${anime_id}`);
  } catch {
    return null;
  }
}
