"""FastAPI routers for Hitcher MVP backend."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_session
from ..models.domain import (
    HookupRequest,
    Location,
    MatchScore,
    RideIntent,
    UserProfile,
    Vector,
    VectorSegment,
)
from ..models.orm import (
    HookupRequestORM,
    RideIntentORM,
    UserORM,
    VectorORM,
    VectorSegmentORM,
    vectors_to_domain,
)
from ..services.matching import find_best_matches, score_match

router = APIRouter()


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.post("/users", status_code=status.HTTP_201_CREATED, response_model=UserProfile)
def create_user(profile: UserProfile, db: Session = Depends(get_session)) -> UserProfile:
    user = UserORM.from_domain(profile)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.to_domain()


@router.get("/users", response_model=List[UserProfile])
def list_users(db: Session = Depends(get_session)) -> List[UserProfile]:
    users = db.query(UserORM).all()
    return [user.to_domain() for user in users]


@router.post("/vectors", status_code=status.HTTP_201_CREATED, response_model=Vector)
def create_vector(vector: Vector, db: Session = Depends(get_session)) -> Vector:
    driver = db.get(UserORM, str(vector.driver_id))
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    orm_vector = VectorORM.from_domain(vector)
    db.add(orm_vector)
    db.commit()
    db.refresh(orm_vector)
    return orm_vector.to_domain()


@router.get("/vectors", response_model=List[Vector])
def list_vectors(db: Session = Depends(get_session)) -> List[Vector]:
    vectors = db.query(VectorORM).all()
    return vectors_to_domain(vectors)


@router.post(
    "/ride-intents",
    status_code=status.HTTP_201_CREATED,
    response_model=RideIntent,
)
def create_ride_intent(intent: RideIntent, db: Session = Depends(get_session)) -> RideIntent:
    rider = db.get(UserORM, str(intent.rider_id))
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")

    orm_intent = RideIntentORM.from_domain(intent)
    db.add(orm_intent)
    db.commit()
    db.refresh(orm_intent)
    return orm_intent.to_domain()


@router.get("/ride-intents", response_model=List[RideIntent])
def list_ride_intents(db: Session = Depends(get_session)) -> List[RideIntent]:
    intents = db.query(RideIntentORM).all()
    return [intent.to_domain() for intent in intents]


@router.post("/match", response_model=List[MatchScore])
def match_vectors(
    ride_intent_id: UUID, limit: int = 5, db: Session = Depends(get_session)
) -> List[MatchScore]:
    intent_record = db.get(RideIntentORM, str(ride_intent_id))
    if not intent_record:
        raise HTTPException(status_code=404, detail="Ride intent not found")

    intent = intent_record.to_domain()
    vectors = db.query(VectorORM).all()
    vector_domains = vectors_to_domain(vectors)
    matches = find_best_matches(vector_domains, intent, limit=limit)
    return matches


@router.post(
    "/hookups",
    status_code=status.HTTP_201_CREATED,
    response_model=HookupRequest,
)
def create_hookup(
    request: HookupRequest, db: Session = Depends(get_session)
) -> HookupRequest:
    vector = db.get(VectorORM, str(request.vector_id))
    if not vector:
        raise HTTPException(status_code=404, detail="Vector not found")
    intent = db.get(RideIntentORM, str(request.ride_intent_id))
    if not intent:
        raise HTTPException(status_code=404, detail="Ride intent not found")

    orm_hookup = HookupRequestORM.from_domain(request)
    db.add(orm_hookup)
    db.commit()
    db.refresh(orm_hookup)
    return orm_hookup.to_domain()


@router.post("/hookups/{hookup_id}/confirm", response_model=HookupRequest)
def confirm_hookup(
    hookup_id: UUID, db: Session = Depends(get_session)
) -> HookupRequest:
    record = db.get(HookupRequestORM, str(hookup_id))
    if not record:
        raise HTTPException(status_code=404, detail="Hook-up request not found")
    record.status = "accepted"
    db.add(record)
    db.commit()
    db.refresh(record)
    return record.to_domain()


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_store(db: Session = Depends(get_session)) -> None:
    """Utility endpoint for testing."""

    db.query(HookupRequestORM).delete()
    db.query(RideIntentORM).delete()
    db.query(VectorSegmentORM).delete()
    db.query(VectorORM).delete()
    db.query(UserORM).delete()
    db.commit()


# Convenience data seeding for manual experimentation
@router.post("/seed", response_model=dict)
def seed_demo_data() -> dict:
    if db.query(UserORM).count():
        return {"message": "Store already seeded", "users": db.query(UserORM).count()}

    driver = UserProfile(full_name="Taylor Driver", is_driver=True)
    rider = UserProfile(full_name="Riley Rider")

    db.add_all([UserORM.from_domain(driver), UserORM.from_domain(rider)])
    db.commit()

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
        desired_start=Location(latitude=30.27, longitude=-97.74),
        desired_end=Location(latitude=30.30, longitude=-97.75),
    )

    orm_vector = VectorORM.from_domain(vector)
    orm_intent = RideIntentORM.from_domain(intent)
    db.add_all([orm_vector, orm_intent])
    db.commit()

    match = score_match(vector, intent)
    return {
        "driver_id": str(driver.id),
        "rider_id": str(rider.id),
        "vector_id": str(vector.id),
        "ride_intent_id": str(intent.id),
        "match_score": match.score,
    }
