"""FastAPI routers for Hitcher MVP backend."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from ..models.domain import (
    HookupRequest,
    MatchScore,
    RideIntent,
    UserProfile,
    Vector,
    VectorSegment,
    Location,
)
from ..services.matching import STORE, find_best_matches, score_match

router = APIRouter()


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserProfile)
def create_user(profile: UserProfile) -> UserProfile:
    STORE.users[profile.id] = profile.to_dict()
    return profile


@router.get("/users", response_model=List[UserProfile])
def list_users() -> List[UserProfile]:
    return [UserProfile.from_dict(stored) for stored in STORE.users.values()]


@router.post("/vectors", status_code=status.HTTP_201_CREATED, response_model=Vector)
def create_vector(vector: Vector) -> Vector:
    if vector.driver_id not in STORE.users:
        raise HTTPException(status_code=404, detail="Driver not found")
    STORE.vectors[vector.id] = vector
    return vector


@router.get("/vectors", response_model=List[Vector])
def list_vectors() -> List[Vector]:
    return list(STORE.vectors.values())


@router.post(
    "/ride-intents",
    status_code=status.HTTP_201_CREATED,
    response_model=RideIntent,
)
def create_ride_intent(intent: RideIntent) -> RideIntent:
    if intent.rider_id not in STORE.users:
        raise HTTPException(status_code=404, detail="Rider not found")
    STORE.ride_intents[intent.id] = intent
    return intent


@router.get("/ride-intents", response_model=List[RideIntent])
def list_ride_intents() -> List[RideIntent]:
    return list(STORE.ride_intents.values())


@router.post("/match", response_model=List[MatchScore])
def match_vectors(ride_intent_id: UUID, limit: int = 5) -> List[MatchScore]:
    intent = STORE.ride_intents.get(ride_intent_id)
    if not intent:
        raise HTTPException(status_code=404, detail="Ride intent not found")
    matches = find_best_matches(STORE.vectors.values(), intent, limit=limit)
    return matches


@router.post(
    "/hookups",
    status_code=status.HTTP_201_CREATED,
    response_model=HookupRequest,
)
def create_hookup(request: HookupRequest) -> HookupRequest:
    if request.vector_id not in STORE.vectors:
        raise HTTPException(status_code=404, detail="Vector not found")
    if request.ride_intent_id not in STORE.ride_intents:
        raise HTTPException(status_code=404, detail="Ride intent not found")
    STORE.hookups[request.id] = request.to_dict()
    return request


@router.post("/hookups/{hookup_id}/confirm", response_model=HookupRequest)
def confirm_hookup(hookup_id: UUID) -> HookupRequest:
    data = STORE.hookups.get(hookup_id)
    if not data:
        raise HTTPException(status_code=404, detail="Hook-up request not found")
    data["status"] = "accepted"
    request = HookupRequest.from_dict(data)
    STORE.hookups[hookup_id] = request.to_dict()
    return request


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_store() -> None:
    """Utility endpoint for testing."""

    STORE.reset()


# Convenience data seeding for manual experimentation
@router.post("/seed", response_model=dict)
def seed_demo_data() -> dict:
    if STORE.users:
        return {"message": "Store already seeded", "users": len(STORE.users)}

    driver = UserProfile(full_name="Taylor Driver", is_driver=True)
    rider = UserProfile(full_name="Riley Rider")

    STORE.users[driver.id] = driver.to_dict()
    STORE.users[rider.id] = rider.to_dict()

    segment = VectorSegment(
        start=Location(latitude=30.2672, longitude=-97.7431),
        end=Location(latitude=30.3072, longitude=-97.755),
        estimated_duration=timedelta(minutes=30),
    )
    vector = Vector(
        driver_id=driver.id,
        departure_time=datetime.utcnow(),
        seats_available=2,
        segments=[segment],
    )
    intent = RideIntent(
        rider_id=rider.id,
        earliest_start=datetime.utcnow(),
        latest_arrival=datetime.utcnow() + timedelta(hours=1),
        desired_start={"latitude": 30.27, "longitude": -97.74},
        desired_end={"latitude": 30.30, "longitude": -97.75},
    )

    STORE.vectors[vector.id] = vector
    STORE.ride_intents[intent.id] = intent

    match = score_match(vector, intent)
    return {
        "driver_id": str(driver.id),
        "rider_id": str(rider.id),
        "vector_id": str(vector.id),
        "ride_intent_id": str(intent.id),
        "match_score": match.score,
    }
