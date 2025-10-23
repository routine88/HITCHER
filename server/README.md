# Hitcher Backend Service

This directory contains the FastAPI-based backend for the Hitcher vector-sharing platform. The initial goal is to provide an experimentation-friendly API that unblocks Android client development while the production architecture evolves.

## Features
- User profile creation and listing (drivers and riders).
- Driver vector publishing with simple validation rules.
- Rider intent submission and retrieval.
- Heuristic-based matching endpoint returning ranked vectors for a rider intent.
- Hook-up request lifecycle with confirmation support.
- Seed and reset utilities to simplify manual QA.

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

## Next Steps
- Replace the in-memory store with a PostGIS-backed persistence layer.
- Integrate authentication and authorization workflows.
- Expand the matching heuristic with real vector geometry scoring.
- Add WebSocket support for chat and live location updates.
