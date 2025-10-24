# Hitcher Backend Service

This directory contains the FastAPI-based backend for the Hitcher vector-sharing platform. The service now persists core entities in SQLite (override with `DATABASE_URL`) so developers can exercise flows end-to-end while the production architecture evolves.

## Features
- User profile creation and listing (drivers and riders).
- Driver vector publishing with simple validation rules and persisted segments.
- Rider intent submission and retrieval stored against user profiles.
- Heuristic-based matching endpoint returning ranked vectors for a rider intent.
- Hook-up request lifecycle with confirmation support.
- Seed and reset utilities to simplify manual QA.

### Persistence

- SQLite database lives at `./hitcher.db` by default. Set `DATABASE_URL` to point at a Postgres/PostGIS instance for richer experimentation.
- Tables are created automatically at startup. `app.db.session_scope()` can be used in scripts for simple migrations or seeding tasks.

## Getting Started
1. Create and activate a virtual environment targeting Python 3.11.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Running Tests
```bash
pytest
```

## API Smoke Testing

Spin up the development server and exercise endpoints:

```bash
uvicorn app.main:app --reload
```

Example operations:

```bash
http POST :8000/users full_name="Demo Driver" is_driver:=true
http POST :8000/vectors driver_id=<driver_id> departure_time=$(date -Iseconds) \
  seats_available:=2 segments:='[{"start": {"latitude": 30.27, "longitude": -97.74}, "end": {"latitude": 30.29, "longitude": -97.76}, "estimated_duration": 900}]'
```

## Next Steps
- Layer SQLAlchemy models on top of a managed PostGIS deployment and introduce Alembic migrations.
- Integrate authentication and authorization workflows.
- Expand the matching heuristic with real vector geometry scoring.
- Add WebSocket support for chat and live location updates.
