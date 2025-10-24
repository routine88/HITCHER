"""Matching heuristics for Hitcher vectors and ride intents."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from ..models.domain import MatchScore, RideIntent, Vector


def _time_overlap_score(vector: Vector, intent: RideIntent) -> float:
    """Compute overlap based on departure and arrival windows."""

    vector_departure = vector.departure_time
    intent_start = intent.earliest_start
    intent_end = intent.latest_arrival

    if vector_departure > intent_end:
        return 0.0

    # assume average trip duration from segments
    total_minutes = sum(
        int(segment.estimated_duration.total_seconds() // 60)
        for segment in vector.segments
    )
    if total_minutes == 0:
        total_minutes = 15

    vector_arrival = vector_departure + vector.segments[0].estimated_duration

    start_diff = abs((vector_departure - intent_start).total_seconds()) / 3600
    arrival_diff = abs((vector_arrival - intent_end).total_seconds()) / 3600

    window_penalty = min(1.0, (start_diff + arrival_diff) / 6)
    return max(0.0, 1.0 - window_penalty)


def _detour_penalty(vector: Vector, intent: RideIntent) -> float:
    """Simple placeholder penalty based on seats and detour tolerance."""

    seat_ratio = min(1.0, intent.seats_needed / vector.seats_available)
    detour_factor = min(1.0, intent.max_detour_minutes / 60)
    return min(1.0, (1 - seat_ratio * 0.5) * (0.5 + detour_factor / 2))


def score_match(vector: Vector, intent: RideIntent) -> MatchScore:
    """Produce a normalized match score between 0 and 1."""

    overlap = _time_overlap_score(vector, intent)
    detour = _detour_penalty(vector, intent)
    score = max(0.0, min(1.0, overlap * detour))

    shared_duration = sum(
        int(segment.estimated_duration.total_seconds() // 60)
        for segment in vector.segments
    )
    pickup_eta = max(0, int((vector.departure_time - datetime.utcnow()).total_seconds() // 60))

    return MatchScore(
        vector_id=vector.id,
        ride_intent_id=intent.id,
        score=score,
        shared_duration_minutes=shared_duration,
        pickup_eta_minutes=pickup_eta,
    )


def find_best_matches(
    vector_pool: Iterable[Vector], intent: RideIntent, limit: int = 5
) -> List[MatchScore]:
    """Return the top scoring vectors for a given ride intent."""

    scores = [score_match(vector, intent) for vector in vector_pool]
    scores.sort(key=lambda match: match.score, reverse=True)
    return scores[:limit]
