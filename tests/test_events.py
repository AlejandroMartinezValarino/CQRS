"""Tests para eventos del dominio."""
import pytest
from datetime import datetime
from common.events.anime_events import ClickRegistered, ViewRegistered, RatingGiven


def test_click_registered_event():
    """Test para el evento ClickRegistered."""
    event = ClickRegistered(
        aggregate_id="anime_1",
        anime_id=1,
        user_id="user123",
        timestamp=datetime.utcnow()
    )
    
    assert event.event_type == "ClickRegistered"
    assert event.anime_id == 1
    assert event.user_id == "user123"
    assert event.aggregate_id == "anime_1"
    assert event.event_id is not None


def test_view_registered_event():
    """Test para el evento ViewRegistered."""
    event = ViewRegistered(
        aggregate_id="anime_1",
        anime_id=1,
        user_id="user123",
        duration_seconds=3600,
        timestamp=datetime.utcnow()
    )
    
    assert event.event_type == "ViewRegistered"
    assert event.duration_seconds == 3600
    assert event.anime_id == 1


def test_rating_given_event():
    """Test para el evento RatingGiven."""
    event = RatingGiven(
        aggregate_id="anime_1",
        anime_id=1,
        user_id="user123",
        rating=9.5,
        timestamp=datetime.utcnow()
    )
    
    assert event.event_type == "RatingGiven"
    assert event.rating == 9.5
    assert 0.0 <= event.rating <= 10.0


def test_rating_validation():
    """Test de validación de rating."""
    event = RatingGiven(
        aggregate_id="anime_1",
        anime_id=1,
        user_id="user123",
        rating=7.5
    )
    assert event.rating == 7.5
    
    with pytest.raises(Exception):
        RatingGiven(
            aggregate_id="anime_1",
            anime_id=1,
            user_id="user123",
            rating=11.0
        )

