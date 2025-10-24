"""SQLAlchemy ORM models for Hitcher backend."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterable
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base
from .domain import (
    HookupRequest,
    Location,
    RideIntent,
    UserProfile,
    Vector,
    VectorSegment,
)


def _uuid_default() -> str:
    return str(uuid4())


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid_default)
    full_name: Mapped[str] = mapped_column(String(255))
    is_driver: Mapped[bool] = mapped_column(default=False)
    vehicle_description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reputation_score: Mapped[float] = mapped_column(default=0.0)
    badges: Mapped[list[str]] = mapped_column(JSON, default=list)

    vectors: Mapped[list["VectorORM"]] = relationship(back_populates="driver")
    ride_intents: Mapped[list["RideIntentORM"]] = relationship(back_populates="rider")

    def to_domain(self) -> UserProfile:
        return UserProfile(
            full_name=self.full_name,
            is_driver=self.is_driver,
            vehicle_description=self.vehicle_description,
            reputation_score=self.reputation_score,
            badges=list(self.badges or []),
            id=UUID(self.id),
        )

    @classmethod
    def from_domain(cls, profile: UserProfile) -> "UserORM":
        return cls(
            id=str(profile.id),
            full_name=profile.full_name,
            is_driver=profile.is_driver,
            vehicle_description=profile.vehicle_description,
            reputation_score=profile.reputation_score,
            badges=list(profile.badges),
        )


class VectorORM(Base):
    __tablename__ = "vectors"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid_default)
    driver_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    departure_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    seats_available: Mapped[int] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    driver: Mapped[UserORM] = relationship(back_populates="vectors")
    segments: Mapped[list["VectorSegmentORM"]] = relationship(
        back_populates="vector", cascade="all, delete-orphan"
    )

    def to_domain(self) -> Vector:
        return Vector(
            driver_id=UUID(self.driver_id),
            departure_time=self.departure_time,
            seats_available=self.seats_available,
            segments=[segment.to_domain() for segment in self.segments],
            notes=self.notes,
            id=UUID(self.id),
        )

    @classmethod
    def from_domain(cls, vector: Vector) -> "VectorORM":
        orm_vector = cls(
            id=str(vector.id),
            driver_id=str(vector.driver_id),
            departure_time=vector.departure_time,
            seats_available=vector.seats_available,
            notes=vector.notes,
        )
        orm_vector.segments = [VectorSegmentORM.from_domain(seg) for seg in vector.segments]
        return orm_vector


class VectorSegmentORM(Base):
    __tablename__ = "vector_segments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid_default)
    vector_id: Mapped[str] = mapped_column(ForeignKey("vectors.id", ondelete="CASCADE"))
    start_latitude: Mapped[float] = mapped_column()
    start_longitude: Mapped[float] = mapped_column()
    end_latitude: Mapped[float] = mapped_column()
    end_longitude: Mapped[float] = mapped_column()
    estimated_duration_seconds: Mapped[int] = mapped_column(Integer)

    vector: Mapped[VectorORM] = relationship(back_populates="segments")

    def to_domain(self) -> VectorSegment:
        return VectorSegment(
            start=Location(latitude=self.start_latitude, longitude=self.start_longitude),
            end=Location(latitude=self.end_latitude, longitude=self.end_longitude),
            estimated_duration=timedelta(seconds=self.estimated_duration_seconds),
        )

    @classmethod
    def from_domain(cls, segment: VectorSegment) -> "VectorSegmentORM":
        return cls(
            start_latitude=segment.start.latitude,
            start_longitude=segment.start.longitude,
            end_latitude=segment.end.latitude,
            end_longitude=segment.end.longitude,
            estimated_duration_seconds=int(segment.estimated_duration.total_seconds()),
        )


class RideIntentORM(Base):
    __tablename__ = "ride_intents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid_default)
    rider_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    earliest_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    latest_arrival: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    desired_start_latitude: Mapped[float] = mapped_column()
    desired_start_longitude: Mapped[float] = mapped_column()
    desired_end_latitude: Mapped[float] = mapped_column()
    desired_end_longitude: Mapped[float] = mapped_column()
    seats_needed: Mapped[int] = mapped_column(Integer, default=1)
    max_detour_minutes: Mapped[int] = mapped_column(Integer, default=10)

    rider: Mapped[UserORM] = relationship(back_populates="ride_intents")
    hookups: Mapped[list["HookupRequestORM"]] = relationship(back_populates="ride_intent")

    __table_args__ = (
        CheckConstraint("latest_arrival > earliest_start", name="ck_intent_time_window"),
    )

    def to_domain(self) -> RideIntent:
        return RideIntent(
            rider_id=UUID(self.rider_id),
            earliest_start=self.earliest_start,
            latest_arrival=self.latest_arrival,
            desired_start=Location(
                latitude=self.desired_start_latitude, longitude=self.desired_start_longitude
            ),
            desired_end=Location(
                latitude=self.desired_end_latitude, longitude=self.desired_end_longitude
            ),
            seats_needed=self.seats_needed,
            max_detour_minutes=self.max_detour_minutes,
            id=UUID(self.id),
        )

    @classmethod
    def from_domain(cls, intent: RideIntent) -> "RideIntentORM":
        return cls(
            id=str(intent.id),
            rider_id=str(intent.rider_id),
            earliest_start=intent.earliest_start,
            latest_arrival=intent.latest_arrival,
            desired_start_latitude=intent.desired_start.latitude,
            desired_start_longitude=intent.desired_start.longitude,
            desired_end_latitude=intent.desired_end.latitude,
            desired_end_longitude=intent.desired_end.longitude,
            seats_needed=intent.seats_needed,
            max_detour_minutes=intent.max_detour_minutes,
        )


class HookupRequestORM(Base):
    __tablename__ = "hookup_requests"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid_default)
    vector_id: Mapped[str] = mapped_column(ForeignKey("vectors.id"))
    ride_intent_id: Mapped[str] = mapped_column(ForeignKey("ride_intents.id"))
    rider_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")

    vector: Mapped[VectorORM] = relationship()
    ride_intent: Mapped[RideIntentORM] = relationship(back_populates="hookups")

    def to_domain(self) -> HookupRequest:
        return HookupRequest(
            vector_id=UUID(self.vector_id),
            ride_intent_id=UUID(self.ride_intent_id),
            rider_message=self.rider_message,
            status=self.status,
            id=UUID(self.id),
        )

    @classmethod
    def from_domain(cls, hookup: HookupRequest) -> "HookupRequestORM":
        return cls(
            id=str(hookup.id),
            vector_id=str(hookup.vector_id),
            ride_intent_id=str(hookup.ride_intent_id),
            rider_message=hookup.rider_message,
            status=hookup.status,
        )


def vectors_to_domain(records: Iterable[VectorORM]) -> list[Vector]:
    return [record.to_domain() for record in records]

