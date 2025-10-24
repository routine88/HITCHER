"""Domain models used across Hitcher backend services."""

from __future__ import annotations

from dataclasses import asdict, field
from datetime import datetime, timedelta
from typing import Dict, List
from uuid import UUID, uuid4


from pydantic.dataclasses import dataclass


@dataclass
class Location:
    """Represents a geospatial coordinate."""

    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not -90.0 <= self.latitude <= 90.0:
            raise ValueError("latitude must be between -90 and 90")
        if not -180.0 <= self.longitude <= 180.0:
            raise ValueError("longitude must be between -180 and 180")

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> "Location":
        return cls(latitude=data["latitude"], longitude=data["longitude"])

    def to_dict(self) -> Dict[str, float]:
        return {"latitude": self.latitude, "longitude": self.longitude}


@dataclass
class VectorSegment:
    """Describes a planned or historical segment of travel."""

    start: Location
    end: Location
    estimated_duration: timedelta = field(default_factory=timedelta)

    def __post_init__(self) -> None:
        if self.estimated_duration < timedelta():
            raise ValueError("estimated_duration must be non-negative")

    @classmethod
    def from_dict(cls, data: Dict) -> "VectorSegment":
        return cls(
            start=Location.from_dict(data["start"]),
            end=Location.from_dict(data["end"]),
            estimated_duration=_coerce_duration(data.get("estimated_duration")),
        )

    def to_dict(self) -> Dict:
        return {
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
            "estimated_duration": self.estimated_duration.total_seconds(),
        }


@dataclass
class UserProfile:
    """Basic profile details used in trust and matching surfaces."""

    full_name: str
    is_driver: bool = False
    vehicle_description: str | None = None
    reputation_score: float = 0.0
    badges: List[str] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not 0.0 <= self.reputation_score <= 5.0:
            raise ValueError("reputation_score must be between 0 and 5")

    def to_dict(self) -> Dict:
        data = asdict(self)
        data["id"] = str(self.id)
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> "UserProfile":
        return cls(
            full_name=data["full_name"],
            is_driver=bool(data.get("is_driver", False)),
            vehicle_description=data.get("vehicle_description"),
            reputation_score=float(data.get("reputation_score", 0.0)),
            badges=list(data.get("badges", [])),
            id=UUID(str(data.get("id", uuid4()))),
        )


@dataclass
class Vector:
    """Represents a driver's available route for sharing."""

    driver_id: UUID
    departure_time: datetime
    seats_available: int
    segments: List[VectorSegment]
    notes: str | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if self.seats_available < 1:
            raise ValueError("seats_available must be at least 1")
        if not self.segments:
            raise ValueError("segments must contain at least one entry")

    @classmethod
    def from_dict(cls, data: Dict) -> "Vector":
        return cls(
            driver_id=UUID(str(data["driver_id"])),
            departure_time=_coerce_datetime(data["departure_time"]),
            seats_available=int(data["seats_available"]),
            segments=[VectorSegment.from_dict(segment) for segment in data["segments"]],
            notes=data.get("notes"),
            id=UUID(str(data.get("id", uuid4()))),
        )

    def to_dict(self) -> Dict:
        return {
            "id": str(self.id),
            "driver_id": str(self.driver_id),
            "departure_time": self.departure_time.isoformat(),
            "seats_available": self.seats_available,
            "segments": [segment.to_dict() for segment in self.segments],
            "notes": self.notes,
        }


@dataclass
class RideIntent:
    """Represents a rider's request for a shared vector."""

    rider_id: UUID
    earliest_start: datetime
    latest_arrival: datetime
    desired_start: Location
    desired_end: Location
    seats_needed: int = 1
    max_detour_minutes: int = 10
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if self.latest_arrival <= self.earliest_start:
            raise ValueError("latest_arrival must be after earliest_start")
        if not 1 <= self.seats_needed <= 4:
            raise ValueError("seats_needed must be between 1 and 4")
        if not 0 <= self.max_detour_minutes <= 60:
            raise ValueError("max_detour_minutes must be between 0 and 60")

    @classmethod
    def from_dict(cls, data: Dict) -> "RideIntent":
        return cls(
            rider_id=UUID(str(data["rider_id"])),
            earliest_start=_coerce_datetime(data["earliest_start"]),
            latest_arrival=_coerce_datetime(data["latest_arrival"]),
            desired_start=Location.from_dict(data["desired_start"]),
            desired_end=Location.from_dict(data["desired_end"]),
            seats_needed=int(data.get("seats_needed", 1)),
            max_detour_minutes=int(data.get("max_detour_minutes", 10)),
            id=UUID(str(data.get("id", uuid4()))),
        )

    def to_dict(self) -> Dict:
        return {
            "id": str(self.id),
            "rider_id": str(self.rider_id),
            "earliest_start": self.earliest_start.isoformat(),
            "latest_arrival": self.latest_arrival.isoformat(),
            "desired_start": self.desired_start.to_dict(),
            "desired_end": self.desired_end.to_dict(),
            "seats_needed": self.seats_needed,
            "max_detour_minutes": self.max_detour_minutes,
        }


@dataclass
class MatchScore:
    """Lightweight structure summarizing compatibility between a vector and ride intent."""

    vector_id: UUID
    ride_intent_id: UUID
    score: float
    shared_duration_minutes: int
    pickup_eta_minutes: int

    def to_dict(self) -> Dict:
        return {
            "vector_id": str(self.vector_id),
            "ride_intent_id": str(self.ride_intent_id),
            "score": self.score,
            "shared_duration_minutes": self.shared_duration_minutes,
            "pickup_eta_minutes": self.pickup_eta_minutes,
        }


@dataclass
class HookupRequest:
    """Represents a rider's hook-up request to a driver."""

    vector_id: UUID
    ride_intent_id: UUID
    rider_message: str | None = None
    status: str = "pending"
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        allowed = {"pending", "accepted", "declined", "cancelled"}
        if self.status not in allowed:
            raise ValueError(f"status must be one of {allowed}")

    @classmethod
    def from_dict(cls, data: Dict) -> "HookupRequest":
        return cls(
            vector_id=UUID(str(data["vector_id"])),
            ride_intent_id=UUID(str(data["ride_intent_id"])),
            rider_message=data.get("rider_message"),
            status=data.get("status", "pending"),
            id=UUID(str(data.get("id", uuid4()))),
        )

    def to_dict(self) -> Dict:
        return {
            "id": str(self.id),
            "vector_id": str(self.vector_id),
            "ride_intent_id": str(self.ride_intent_id),
            "rider_message": self.rider_message,
            "status": self.status,
        }


def _coerce_datetime(value) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def _coerce_duration(value) -> timedelta:
    if isinstance(value, timedelta):
        return value
    if isinstance(value, (int, float)):
        return timedelta(seconds=float(value))
    if isinstance(value, str):
        parts = value.split(":")
        hours, minutes, seconds = (int(part) for part in parts)
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
    raise ValueError("Unsupported duration type")
