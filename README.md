# 🎌 IndoAnimeList — India's Anime Leaderboard

A full-stack web application that crowdsources ratings from Indian users to generate a Bayesian-ranked Top 50 anime leaderboard from a curated catalog of 500 titles.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.11+) |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| ORM | SQLAlchemy 2.0 + Alembic |
| Frontend | Next.js 14 (App Router) |
| Auth | JWT (httpOnly cookies) |
| Geofencing | ip-api.com |
| Email | Resend |
| Images | Cloudflare R2 |
| Anime Data | Jikan API v4 (one-time seeding) |

---

## Project Structure

```
IndoAList/
├── backend/            # FastAPI app
│   ├── app/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   └── services/
│   ├── scripts/
│   │   └── seed.py
│   ├── alembic/
│   ├── requirements.txt
│   └── .env.example
├── frontend/           # Next.js app
│   ├── app/
│   ├── components/
│   └── lib/
└── docker-compose.yml  # Local dev: PostgreSQL + Redis
```

---

## Local Development Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker + Docker Compose

### 1. Start the database and Redis

```bash
docker-compose up -d
```

### 2. Set up the backend

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your actual values

# Run database migrations
alembic upgrade head

# Seed the database with 500 anime (run once)
python -m scripts.seed

# Start the API server
uvicorn app.main:app --reload --port 8000
```

### 3. Set up the frontend

```bash
cd frontend

# Install dependencies (already done if you ran npm)
npm install

# Start dev server
npm run dev
```

The app will be available at:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `JWT_SECRET` | Long random string for JWT signing |
| `RESEND_API_KEY` | Resend API key for emails |
| `R2_ACCOUNT_ID` | Cloudflare account ID |
| `R2_ACCESS_KEY` | R2 access key |
| `R2_SECRET_KEY` | R2 secret key |
| `R2_BUCKET_NAME` | R2 bucket name |
| `R2_PUBLIC_URL` | Public URL for R2 bucket |
| `ADMIN_API_KEY` | Admin endpoint protection key |

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/api/leaderboard` | None | Top 50 (Redis cached) |
| GET | `/api/anime/search?q=` | None | Fuzzy search catalog |
| GET | `/api/anime/{id}` | None | Anime detail |
| POST | `/api/rate` | JWT | Submit/update rating |
| GET | `/api/rate/{id}` | JWT | Get your rating |
| POST | `/api/auth/register` | None | Register (India-only) |
| GET | `/api/auth/verify` | None | Verify email |
| POST | `/api/auth/login` | None | Login |
| POST | `/api/auth/logout` | None | Logout |
| POST | `/api/auth/refresh` | None | Refresh JWT |
| GET | `/api/auth/me` | JWT | Current user |
| GET | `/api/admin/stats` | Admin Key | Site stats |
| GET | `/api/admin/config` | Admin Key | Ranking config |

---

## Bayesian Ranking Formula

$$\text{Score} = \frac{v \cdot R + m \cdot C}{v + m}$$

- **v** = vote count for the anime
- **R** = simple arithmetic mean
- **m** = minimum vote threshold (default: 25)
- **C** = global mean across all rated anime (dynamic)

---

## Deployment

| Service | Platform |
|---|---|
| Frontend | Vercel (connect GitHub repo) |
| Backend + DB + Redis | Railway (create services from repo) |
| Images | Cloudflare R2 |

---

*IndoAnimeList v1.0 — Built with ❤️ for India's anime community*
