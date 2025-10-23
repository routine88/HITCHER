from datetime import datetime, timedelta

from uuid import UUID

from app.models.domain import Location, RideIntent, Vector, VectorSegment
from app.services.matching import find_best_matches, score_match


def make_vector(departure: datetime, minutes: int = 30):
    segment = VectorSegment(
        start=Location(latitude=30.0, longitude=-97.0),
        end=Location(latitude=30.1, longitude=-97.1),
        estimated_duration=timedelta(minutes=minutes),
    )
    return Vector(
        driver_id=UUID("11111111-1111-1111-1111-111111111111"),
        departure_time=departure,
        seats_available=2,
        segments=[segment],
    )


def make_intent(start: datetime, end: datetime):
    return RideIntent(
        rider_id=UUID("22222222-2222-2222-2222-222222222222"),
        earliest_start=start,
        latest_arrival=end,
        desired_start=Location(latitude=30.02, longitude=-97.02),
        desired_end=Location(latitude=30.12, longitude=-97.12),
    )


def test_score_match_returns_normalized_value():
    vector = make_vector(datetime.utcnow())
    intent = make_intent(datetime.utcnow(), datetime.utcnow() + timedelta(hours=1))

    score = score_match(vector, intent)

    assert 0.0 <= score.score <= 1.0
    assert score.shared_duration_minutes > 0


def test_find_best_matches_sorts_by_score():
    now = datetime.utcnow()
    vector_a = make_vector(now)
    vector_b = make_vector(now + timedelta(hours=3))
    intent = make_intent(now, now + timedelta(hours=2))

    matches = find_best_matches([vector_a, vector_b], intent, limit=2)

    assert len(matches) == 2
    assert matches[0].score >= matches[1].score
