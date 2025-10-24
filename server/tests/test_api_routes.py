"""Integration tests for FastAPI routes using an in-memory SQLite database."""

from __future__ import annotations

from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, get_session
from app.main import create_app


def setup_test_app():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    app = create_app()

    def override_get_session() -> Session:
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    return app


def test_create_user_and_vector_flow():
    app = setup_test_app()
    client = TestClient(app)

    user_payload = {"full_name": "Test Driver", "is_driver": True}
    resp = client.post("/users", json=user_payload)
    assert resp.status_code == 201
    driver = resp.json()

    vector_payload = {
        "driver_id": driver["id"],
        "departure_time": datetime.utcnow().isoformat(),
        "seats_available": 2,
        "segments": [
            {
                "start": {"latitude": 30.27, "longitude": -97.74},
                "end": {"latitude": 30.28, "longitude": -97.75},
                "estimated_duration": timedelta(minutes=15).total_seconds(),
            }
        ],
    }
    resp = client.post("/vectors", json=vector_payload)
    assert resp.status_code == 201, resp.text
    vector = resp.json()
    assert vector["driver_id"] == driver["id"]

    rider_resp = client.post("/users", json={"full_name": "Test Rider"})
    rider_resp.raise_for_status()
    rider = rider_resp.json()

    intent_payload = {
        "rider_id": rider["id"],
        "earliest_start": datetime.utcnow().isoformat(),
        "latest_arrival": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
        "desired_start": {"latitude": 30.27, "longitude": -97.74},
        "desired_end": {"latitude": 30.29, "longitude": -97.76},
        "seats_needed": 1,
        "max_detour_minutes": 15,
    }
    intent_resp = client.post("/ride-intents", json=intent_payload)
    assert intent_resp.status_code == 201
    intent = intent_resp.json()

    match_resp = client.post(
        "/match",
        params={"ride_intent_id": intent["id"], "limit": 3},
    )
    match_resp.raise_for_status()
    matches = match_resp.json()
    assert len(matches) == 1
    assert matches[0]["vector_id"] == vector["id"]


def test_create_and_confirm_hookup():
    app = setup_test_app()
    client = TestClient(app)

    driver = client.post("/users", json={"full_name": "Driver", "is_driver": True}).json()
    rider = client.post("/users", json={"full_name": "Rider"}).json()

    vector = client.post(
        "/vectors",
        json={
            "driver_id": driver["id"],
            "departure_time": datetime.utcnow().isoformat(),
            "seats_available": 1,
            "segments": [
                {
                    "start": {"latitude": 30.0, "longitude": -97.7},
                    "end": {"latitude": 30.1, "longitude": -97.8},
                    "estimated_duration": timedelta(minutes=20).total_seconds(),
                }
            ],
        },
    ).json()

    intent = client.post(
        "/ride-intents",
        json={
            "rider_id": rider["id"],
            "earliest_start": datetime.utcnow().isoformat(),
            "latest_arrival": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            "desired_start": {"latitude": 30.0, "longitude": -97.7},
            "desired_end": {"latitude": 30.1, "longitude": -97.8},
        },
    ).json()

    hookup_resp = client.post(
        "/hookups",
        json={
            "vector_id": vector["id"],
            "ride_intent_id": intent["id"],
            "rider_message": "Ready to ride",
        },
    )
    hookup_resp.raise_for_status()
    hookup = hookup_resp.json()
    assert hookup["status"] == "pending"

    confirm_resp = client.post(f"/hookups/{hookup['id']}/confirm")
    confirm_resp.raise_for_status()
    confirmed = confirm_resp.json()
    assert confirmed["status"] == "accepted"

