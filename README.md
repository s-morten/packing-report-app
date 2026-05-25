Project Overview
Vision

Build a responsive, web-based “Bloomberg terminal” for sharp German soccer bettors.

The application will:

    Compare pre‑match odds for German soccer leagues across multiple bookmakers.

    Allow users to manually track their bets.

    Provide basic analytics, including a profit curve and key performance metrics.

Target Users and Scope

    Primary users: Sharp / semi‑pro bettors interested in value and performance tracking.

    Sport: Soccer only.

    Region: German leagues (e.g. Bundesliga, 2. Bundesliga, etc.).

    Bookmakers: 2–3 bookmakers available via a free odds API.

    Devices: Responsive web app, natively usable on both mobile and desktop.

Core MVP Features
1. Odds Comparison

    Select sport (soccer), league (e.g. Bundesliga), and match.

    Display pre‑match odds from multiple bookmakers in a single table.

    Highlight the best odds per outcome (e.g. home/draw/away).

    Data source: free sports odds API (limited to free tier constraints).

2. Bet Tracking

    Manually add bets with:

        Bookmaker, stake, odds, sport, league, match, outcome, placed_at.

    View a list of bets with status:

        Open, won, lost, void.

    Update bets when results are known.

3. Analytics

    Aggregate stats over a selected date range:

        Profit, ROI, yield, hit rate, drawdown.

    Simple charts:

        Profit curve over time.

        (Optional later) breakdowns by league or bookmaker.

Architecture

    Monorepo:

        /apps/web: Frontend (TypeScript, React/Next.js).

        /apps/api: Backend (Python, FastAPI).

        /packages/shared: Shared types and utilities (optional but recommended).

        /infra: Dockerfiles, docker-compose, infra scripts.

    Database:

        PostgreSQL for dev and prod (local via Docker; hosted via a free-tier provider).

    Odds ingestion:

        One free odds API providing soccer odds for German leagues and 2–3 bookmakers.

        Scheduled ingestion of pre‑match odds snapshots.

Data Model (High Level)

Main entities:

    sport

    league

    team

    event (matches)

    bookmaker

    market (e.g. 1X2)

    market_outcome (home/draw/away)

    odds_snapshot (odds over time)

    user

    bet

These tables are implemented via SQLAlchemy models and managed via Alembic migrations on PostgreSQL.
Actionable Steps (For a Coding Agent)
1. Repository and Tooling Setup

1.1 Create monorepo structure:

    apps/web

    apps/api

    packages/shared (optional)

    infra

1.2 Configure tooling:

    Frontend:

        TypeScript, ESLint, Prettier.

    Backend:

        Python, FastAPI, Black, isort, linting (e.g. flake8 or ruff).

    Root-level README and basic project description.

1.3 Docker & local dev:

    Add docker-compose.yml with:

        web service (frontend).

        api service (backend).

        postgres service (local DB).

    Ensure docker-compose up starts a working skeleton (health endpoints).

2. Backend: FastAPI + PostgreSQL

2.1 FastAPI skeleton:

    Create main.py with:

        FastAPI app.

        /health endpoint (simple JSON OK response).

2.2 DB configuration:

    Install SQLAlchemy and PostgreSQL driver (psycopg/psycopg2).

    Implement DB session handling:

        SessionLocal bound to Postgres engine.

        Dependency for injecting DB sessions into routes.

2.3 Data models:

    Implement SQLAlchemy models for:

        sport, league, team, event.

        bookmaker, market, market_outcome, odds_snapshot.

        user, bet.

2.4 Migrations:

    Set up Alembic.

    Generate initial migration creating all core tables.

    Apply migration to local Postgres via Docker.

3. Odds Ingestion Module

3.1 Integrate a free odds API:

    Configure base URL and API key via environment variables.

    Verify coverage of:

        Soccer.

        German leagues (Bundesliga, etc.).

        At least 2–3 bookmakers in the free tier.

3.2 Implement ingestion logic:

    Normalize and upsert:

        Leagues into league.

        Teams into team.

        Events into event (home_team, away_team, start_time).

    Fetch odds for upcoming events:

        Map to market and market_outcome (e.g. 1X2).

        Insert odds_snapshot entries with bookmaker, outcome, odds, timestamp.

3.3 Scheduling:

    Implement a CLI or script odds_ingestion.py that:

        Runs the ingestion pipeline once.

    (Later) Hook this into a scheduler (cron/job runner) for periodic updates.

4. Backend API Endpoints

4.1 Odds endpoints:

    GET /leagues:

        Returns list of leagues (id, name, country).

    GET /events?league_id=:

        Returns upcoming events for a league (id, teams, start_time).

    GET /odds?event_id=:

        Returns latest odds per bookmaker and outcome for the event.

4.2 Bet endpoints:

    POST /bets:

        Payload: bookmaker_id, event_id, market_outcome_id, stake, odds, placed_at.

        Creates bet entry (status default open).

    GET /bets:

        Returns user’s bets with filters (e.g. date range).

    (Optional) PATCH /bets/{id}:

        Update result and payout once the bet is settled.

4.3 Stats endpoint:

    GET /stats?from=&to=:

        Computes:

            Total profit.

            ROI.

            Yield.

            Hit rate.

            Drawdown.

        Returns data for plotting a profit curve (time series of cumulative profit).

5. Frontend: Responsive UI

5.1 Frontend skeleton:

    Initialize Next.js (or similar) app in apps/web.

    Set up routing and layout with navigation:

        “Odds”

        “My Bets”

        “Analytics”

5.2 Responsive design:

    Use a mobile‑first CSS framework (e.g. Tailwind).

    Ensure odds tables and forms render nicely on:

        Small screens (stacked or horizontally scrollable tables).

        Large screens (full tables).

5.3 Odds page:

    Integrate with backend:

        Fetch leagues -> league dropdown.

        Fetch events -> match selection.

        Fetch odds -> odds table.

    Highlight best odds per outcome.

5.4 My Bets page:

    Bet creation form:

        Fields: bookmaker, match, outcome, stake, odds, placed_at.

        Submit via POST /bets.

    Bet list:

        Fetch via GET /bets.

        Show status and key fields.

5.5 Analytics:

    Fetch stats via GET /stats.

    Display:

        Profit curve chart (using a charting library).

        Summary metrics (profit, ROI, yield, drawdown).

6. Deployment

6.1 Postgres hosting:

    Create a free-tier Postgres instance (e.g. Neon, Supabase, Fly.io).

    Set DATABASE_URL for production.

6.2 Backend deployment:

    Containerize the FastAPI app (Dockerfile).

    Deploy to a small PaaS or VPS.

    Configure environment variables (API keys, DB URL).

6.3 Frontend deployment:

    Deploy the Next.js app to a hosting platform (e.g. Vercel or similar).

    Configure API base URL pointing to the deployed backend.

6.4 Final verification:

    Run ingestion against production DB.

    Verify:

        Leagues and events appear in frontend.

        Odds comparison works.

        Bet creation, listing, and analytics work end‑to‑end.