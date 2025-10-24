# Hitcher: Where to Go From Here

## Current Snapshot
- **Documentation**: `docs/PRD.md` captures the product vision, MVP scope, architecture, and the local testing workflows that were added alongside the persistence work. `README.md` plus component-specific READMEs orient you around the repo structure and available commands.
- **Backend (`server/`)**: FastAPI app wired to an SQLite database via SQLAlchemy. Routes cover user onboarding, vector publishing, rider intents, matching, and hook-up confirmations. Integration tests exist (`tests/test_api_routes.py`, `tests/test_matching.py`).
- **Android Client (`android/`)**: Kotlin MVVM skeleton with Gradle wrapper, placeholder UI, and repositories ready to call the backend when APIs are stable.

## Local Environment Bring-Up
1. **Clone & Navigate**: `git clone` the repo, then `cd HITCHER`.
2. **Python Backend**:
   - Ensure Python 3.11 is installed.
   - Create a virtualenv: `python3.11 -m venv .venv && source .venv/bin/activate`.
   - Install deps: `pip install -r server/requirements.txt` (FastAPI, Pydantic, SQLAlchemy, etc.).
   - Apply schema (auto-migrates on boot) by launching the API: `cd server && uvicorn app.main:app --reload`.
   - Override `DATABASE_URL` if you want a persistent Postgres/PostGIS instance.
3. **Android App**:
   - Open `android/` in Android Studio (Gradle wrapper bundled).
   - Sync Gradle, choose a device/emulator running API 24+.
   - Use `./gradlew testDebug` for unit tests and plan instrumentation once UI flows land.

## Testing Status & Immediate Actions
- Latest CI attempt failed because FastAPI/Pydantic were missing in the execution environment. After installing dependencies locally via `pip install -r server/requirements.txt`, rerun:
  ```bash
  cd server
  pytest
  ```
  Confirm all API and matching tests pass. If failures persist, inspect SQLAlchemy session setup and JSON schemas introduced in `app/api/routes.py`.
- No Android tests exist yet; once networking and view models are implemented, add coverage under `android/app/src/test/` and validate with `./gradlew test`.

## Roadmap for the Next Contributor / AI
1. **Stabilize Backend Persistence**
   - Finalize ORM relationships (e.g., cascades, constraints) and consider migrations (Alembic) before production.
   - Harden request/response models with Pydantic validators and consistent error handling.
   - Enrich matching logic with geospatial scoring leveraging stored vector segments.
2. **Authentication & Profiles**
   - Introduce auth (JWT or OAuth) so hook-up confirmations are secure.
   - Extend feedback profile data structures (ratings, comments) and surface them via API.
3. **Android Integration**
   - Implement Retrofit service matching the backend contracts.
   - Wire `VectorViewModel` to fetch vectors/rider intents, add Compose/Views for publishing and requesting rides.
   - Add instrumentation tests once flows are interactive.
4. **Developer Experience**
   - Containerize backend (Dockerfile + docker-compose) bundling database.
   - Automate lint/test via GitHub Actions once dependencies install cleanly in CI.

## How to Engage as the Next Agent
- Start by running backend tests locally to ensure a green baseline.
- If expanding features, update both code and `docs/PRD.md` so the roadmap stays aligned.
- Document new commands or caveats in the relevant README and amend this guide if the onboarding path changes.

Stay disciplined about pairing code updates with tests—especially around matching and persistence—as we expand functionality.
