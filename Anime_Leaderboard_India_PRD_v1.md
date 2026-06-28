# Product Requirements Document
## Anime Leaderboard (India) — Version 1.0 (MVP)

**Status:** Draft  
**Scope:** India-only user base

---

## 1. Executive Summary

The objective of V1 is to launch a streamlined, highly focused web application that crowdsources ratings exclusively from Indian users to generate a mathematically accurate Top 50 anime leaderboard.

To ensure high data density and avoid the cold-start problem, the initial catalog is strictly constrained to the Top 500 globally recognised anime (sourced from MyAnimeList). Registration is open to users accessing the site from Indian IP addresses only, enforced via IP geofencing. The leaderboard and catalog remain publicly viewable by anyone.

---

## 2. User Roles & Permissions

| Role | Permissions | Auth Requirement |
|---|---|---|
| Guest (Unauthenticated) | Read-only: view leaderboard, search catalog, view aggregate scores | None — open access |
| Registered User (Authenticated) | All Guest actions + submit / update personal ratings (1–10) for any catalog title | Email + password — registration blocked for non-Indian IPs via geofencing |

> **Note:** Registration is restricted to users accessing the site from an Indian IP address, enforced via IP geofencing (MaxMind GeoLite2 or equivalent). Users on VPNs may bypass this, which is an accepted limitation for V1. The leaderboard and catalog remain publicly viewable by anyone globally.

---

## 3. Core Features & Specifications

### 3.1 Curated Catalog (Seed Data)

- **Dataset:** The application database will be pre-seeded with exactly 500 records representing the Top 500 anime sourced from MyAnimeList (via the Jikan API or an equivalent dataset).
- **Seed Strategy:** A one-time seeding script will be run at launch. Cover images will be stored locally (not hotlinked from MAL) to ensure reliability and avoid third-party dependency on image availability.
- **Searchability:** All 500 titles are searchable — including those that have not yet qualified for the leaderboard.

### 3.2 Leaderboard Module (The "Top 50")

- **Capacity:** Displays a maximum of 50 anime at any time.
- **Ranking Algorithm:** Strictly ordered by Bayesian Weighted Average. A title must meet a minimum vote threshold (`m`) to qualify. `m` is set at 25 votes and is configurable via an admin environment variable.
- **Data Displayed per entry:**
  - Rank (1–50)
  - Anime title and cover image
  - Bayesian Average Rating (the "Trusted Score")
  - Total user vote count

### 3.3 Search & Discovery Module

- **Functionality:** Allows any visitor (authenticated or not) to search the full 500-title catalog.
- **Data Displayed (Standard View)** — for titles below the vote threshold or not yet on the leaderboard:
  - Anime title and cover image
  - Simple Average Rating (arithmetic mean of all submitted ratings)
  - Total user vote count

> **Note:** Titles below the minimum vote threshold intentionally display the simple average rather than the Bayesian score. This accurately reflects raw local sentiment without distorting the curated Top 50.

### 3.4 Rating & Authentication Engine

#### Authentication Flow

- Sign-up requires a valid email address and password. No phone number is collected.
- At the point of registration, the user's IP address is checked against a geolocation database (e.g. MaxMind GeoLite2). If the IP resolves to a non-Indian location, the registration request is rejected with a clear error message.
- On successful registration, a JWT is issued and stored client-side (`httpOnly` cookie recommended).
- Email verification (magic link or confirmation email) is required before a user can submit ratings, to prevent throwaway account spam.

#### Rating Rules

- All `POST /api/rate` requests are JWT-protected. Unauthenticated requests surface a login / register modal client-side.
- Ratings are integers from 1 to 10 (inclusive).
- A single User ID may hold exactly one active rating per Anime ID. Submitting a new rating overwrites the previous one for that title.
- Deleted accounts: ratings are anonymised (`user_id` set to `null`) but retained to preserve leaderboard integrity.

#### Security Notes

- Geofencing is enforced at registration only, not on every request. A user who registers from India and later accesses the site via VPN is permitted — the gate is at the door, not throughout the session.
- JWT expiry should be set to 7 days with refresh token support to avoid forcing frequent re-authentication.
- Rate-limit registration attempts per IP to prevent abuse (e.g. max 5 registration attempts per IP per hour).

---

## 4. Open Technical Questions

The following items require a decision before development begins:

- **Geofencing database:** MaxMind GeoLite2 (free, self-hosted) vs GeoIP2 (paid, more accurate) vs a third-party API (ipapi.co, ip-api.com). Confirm before development.
- **Email provider:** Which service will handle transactional email for verification links (e.g. Resend, SendGrid, AWS SES)?
- **Image storage:** Confirm S3-compatible bucket or local volume for cover image hosting.
- **Vote threshold (`m`):** Defaulting to 25 — confirm this with the team before launch.
- **Bayesian prior mean (`C`):** The global mean across all rated titles in the catalog. Confirm whether this is computed dynamically or set as a fixed prior at launch.

---

## 5. Out of Scope for Version 1

The following features are deferred to V2 or later to ensure a rapid launch and validation of the core rating mechanic.

| Feature | Description | Target |
|---|---|---|
| Custom Playlists | "Plan to Watch", "Favorites" lists | V2 |
| Text Reviews | Granular written comments on titles | V2 |
| Social Features | Following users, sharing lists, activity feed | V2 |
| Catalog Expansion | Beyond initial Top 500 MAL seed | V2 |
| Stricter Geo-enforcement | Phone OTP or stronger identity verification for Indian users | V2+ |

---

*Anime Leaderboard India — PRD v1.0 — Internal Draft*
