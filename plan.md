# Packing Report App — Implementation Plan

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15 (App Router), TypeScript, Tailwind CSS, React Query |
| Backend | Python 3.12+, FastAPI, async SQLAlchemy 2.0 + asyncpg |
| Database | PostgreSQL |
| Monorepo | pnpm workspaces + Turborepo (JS), uv (Python) |
| Auth | JWT (email + password), httpOnly cookies |
| Odds API | the-odds-api.com |
| Dev infra | Docker Compose (api + web + postgres + redis) |
| CI | GitHub Actions (lint, typecheck, test, build) |
| Deployment | Containerized → any PaaS (Render, Fly.io, Railway) |

---

## Project Structure

```
packing-report-app/
├── apps/
│   ├── api/                          # FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py               # FastAPI app, middleware, lifespan
│   │   │   ├── core/
│   │   │   │   ├── config.py         # Pydantic-settings (env validation)
│   │   │   │   ├── database.py       # Async SQLAlchemy engine + sessions
│   │   │   │   ├── security.py       # JWT create/verify
│   │   │   │   ├── logging.py        # Structured JSON logging
│   │   │   │   └── exceptions.py     # Consistent error format
│   │   │   ├── modules/              # Feature modules
│   │   │   │   ├── auth/             # Register, login, token refresh
│   │   │   │   ├── odds/             # Leagues, events, odds endpoints + ingestion
│   │   │   │   ├── bets/             # Bet CRUD
│   │   │   │   └── analytics/        # Stats computation
│   │   │   └── models/               # SQLAlchemy models (shared across modules)
│   │   ├── alembic/                  # DB migrations
│   │   ├── tests/
│   │   │   ├── conftest.py
│   │   │   ├── unit/
│   │   │   └── integration/
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   └── Dockerfile.dev
│   │
│   └── web/                          # Next.js frontend
│       ├── src/
│       │   ├── app/                  # Routes only (file-system routing)
│       │   │   ├── layout.tsx
│       │   │   ├── page.tsx
│       │   │   ├── (dashboard)/
│       │   │   │   ├── odds/page.tsx
│       │   │   │   ├── bets/page.tsx
│       │   │   │   └── analytics/page.tsx
│       │   │   └── api/              # Next.js API route proxies
│       │   ├── components/
│       │   │   ├── ui/               # Button, Table, Select, Card, etc.
│       │   │   ├── layout/           # Navbar, Sidebar, MobileDrawer
│       │   │   ├── odds/             # OddsTable, BestOddsBadge
│       │   │   ├── bets/             # BetForm, BetList, BetStatusBadge
│       │   │   └── analytics/        # ProfitChart, MetricsGrid
│       │   ├── lib/
│       │   │   ├── api-client.ts     # Typed fetch wrapper
│       │   │   └── utils.ts          # Formatters
│       │   ├── hooks/                # React Query wrappers
│       │   └── types/
│       ├── next.config.ts
│       ├── tailwind.config.ts
│       ├── Dockerfile
│       └── package.json
│
├── packages/
│   └── shared/                       # Enums, constants, shared TS types
│       ├── src/
│       │   ├── types/
│       │   └── constants.ts
│       ├── package.json
│       └── tsconfig.json
│
├── infra/
│   ├── docker-compose.yml            # Dev: api + web + postgres + redis
│   ├── docker-compose.prod.yml
│   └── .env.example
│
├── .github/
│   └── workflows/ci.yml              # Lint, typecheck, test, build
├── .husky/                           # Pre-commit hooks
│   ├── pre-commit
│   └── commit-msg
├── pnpm-workspace.yaml
├── turbo.json
├── .prettierrc
├── .eslintrc.js
└── .gitignore
```

---

## Data Model

Main entities (implemented as async SQLAlchemy 2.0 models):

- **sport** — id, name, slug
- **league** — id, sport_id, name, country, external_id
- **team** — id, name, external_id
- **event** — id, league_id, home_team_id, away_team_id, start_time, status, external_id
- **bookmaker** — id, name, external_id
- **market** — id, name (e.g. "1X2"), external_id
- **market_outcome** — id, market_id, name (home/draw/away), external_id
- **odds_snapshot** — id, event_id, bookmaker_id, market_outcome_id, odds, captured_at
- **user** — id, email, password_hash, created_at
- **bet** — id, user_id, bookmaker_id, event_id, market_outcome_id, stake, odds, status (open/won/lost/void), placed_at, settled_at

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /auth/register | No | Create account |
| POST | /auth/login | No | Get JWT tokens |
| POST | /auth/refresh | Yes | Refresh access token |
| GET | /leagues | No | List available leagues |
| GET | /events?league_id= | No | Upcoming events for league |
| GET | /odds?event_id= | No | Latest odds per bookmaker |
| POST | /bets | Yes | Place a bet |
| GET | /bets?offset=&limit=&from=&to= | Yes | List user's bets (paginated) |
| PATCH | /bets/{id} | Yes | Update bet result |
| GET | /stats?from=&to= | Yes | Profit, ROI, yield, hit rate, drawdown + time series |
| GET | /health | No | DB connectivity + last ingestion |

All errors return: `{"error": {"code": "string", "message": "string"}}`

---

## Testing Strategy

| Layer | Tool | Scope |
|-------|------|-------|
| Python unit | pytest | Services, repo layer (in-memory DB) |
| Python integration | pytest + testcontainers | Full endpoint flow against real Postgres |
| Python coverage | pytest-cov | Target ≥80% |
| JS unit | Vitest + @testing-library/react | Components, hooks, utils |
| JS e2e | Playwright | Critical path: odds → bet → analytics |
| CI | GitHub Actions | Parallel: lint, typecheck, test, build |

---

## Implementation Phases

### Phase 1 — Foundation
- Monorepo scaffold (pnpm workspaces, Turborepo, uv)
- Docker Compose (api + web + postgres + redis)
- FastAPI skeleton with `/health`, CORS, lifespan
- Pydantic-settings for env config
- Async SQLAlchemy engine + session management
- SQLAlchemy models for all entities
- Alembic init + initial migration
- JWT auth module (register, login, refresh)
- Next.js scaffold with App Router, Tailwind
- Shared types package
- Pre-commit hooks (husky, commitlint, lint-staged)
- GitHub Actions CI

### Phase 2 — Odds Ingestion
- the-odds-api.com client (fetch leagues, events, odds)
- Upsert logic (normalize external data into local schema)
- CLI entry point: `python -m app.modules.odds.tasks --ingest`
- Background scheduler (ARQ) for periodic ingestion

### Phase 3 — Core API Endpoints
- `GET /leagues`, `GET /events`, `GET /odds`
- `POST /bets`, `GET /bets`, `PATCH /bets/{id}`
- `GET /stats` (profit, ROI, yield, hit rate, drawdown, time series)
- Pagination, consistent error responses

### Phase 4 — Frontend UI
- Odds comparison page (league dropdown → match select → odds table with best-odds highlighting)
- Bet tracking page (form + list with filters)
- Analytics page (profit curve chart + metric cards)
- Responsive design (mobile-first with Tailwind)
- Loading states (`loading.tsx`), error boundaries (`error.tsx`)

### Phase 5 — Polish & Deploy
- React Query for client-side mutations + cache invalidation
- Server Actions for bet form submission
- OpenAPI codegen (types from FastAPI schema)
- Multi-stage Docker builds
- Deploy to PaaS
- E2E tests with Playwright

---

## Key Design Decisions

1. **Async everything** — FastAPI + async SQLAlchemy + asyncpg; no blocking calls in request path
2. **Feature modules** — Each domain (auth, odds, bets, analytics) is self-contained with router, service, schemas
3. **Server Components by default** — Initial data fetches on server; React Query for mutations and stale data
4. **JWT in httpOnly cookies** — Prevents XSS token theft; refresh token rotation
5. **Upsert ingestion** — `ON CONFLICT ... DO UPDATE` avoids duplicates on re-import
6. **Background queue for ingestion** — ARQ with Redis; doesn't block API responses
7. **Consistent error contract** — Single error format across all endpoints
8. **Rate limiting on POST endpoints** — Prevent abuse of bet creation
9. **Pre-commit enforcement** — Code that doesn't pass lint/typecheck never gets committed
10. **CI gates on every PR** — Lint → typecheck → test → build must pass before merge
