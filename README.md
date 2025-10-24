# HITCHER

Hitcher is a vector-sharing platform enabling riders and drivers travelling in similar directions to hook up for shared trips. This repository now contains the living Product Requirements Document, a FastAPI backend service scaffold, and a native Android application skeleton.

## Repository Structure

- `docs/PRD.md` — Product requirements and implementation roadmap.
- `server/` — FastAPI backend with SQLite persistence, heuristic matching, hook-up workflows, and pytest coverage.
- `android/` — Kotlin Android project with MVVM scaffolding for Explore-style status UI.

## Getting Started

Follow the individual READMEs in `server/` and `android/` for environment setup instructions.

## Local Testing Overview

The repository already ships with basic workflows to exercise each surface locally:

- **Backend** — from the `server/` directory create a Python 3.11 virtualenv, install dependencies, and run `pytest` for service coverage (API + heuristics). Launch the development server with `uvicorn app.main:app --reload` to test endpoints against the bundled SQLite database, or set `DATABASE_URL` for Postgres/PostGIS experimentation.
- **Android App** — from the `android/` directory use the Gradle wrapper (`./gradlew`) provided in the repo. Sync the project in Android Studio to run it on an emulator/device and execute `./gradlew testDebug` (or `test` for all variants) to verify view model and repository units as they are added.

Refer to the component READMEs for deeper instructions and upcoming testing enhancements (instrumentation, integration suites).
