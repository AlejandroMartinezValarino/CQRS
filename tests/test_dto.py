"""Tests para DTOs."""
import pytest
from common.dto.command_dto import ClickCommand, ViewCommand, RatingCommand


def test_click_command():
    """Test para ClickCommand."""
    command = ClickCommand(anime_id=1, user_id="user123")
    
    assert command.anime_id == 1
    assert command.user_id == "user123"


def test_view_command():
    """Test para ViewCommand."""
    command = ViewCommand(
        anime_id=1,
        user_id="user123",
        duration_seconds=3600
    )
    
    assert command.anime_id == 1
    assert command.duration_seconds == 3600


def test_rating_command():
    """Test para RatingCommand."""
    command = RatingCommand(
        anime_id=1,
        user_id="user123",
        rating=9.5
    )
    
    assert command.rating == 9.5


def test_view_command_validation():
    """Test de validación de ViewCommand."""
    # Duración negativa debería fallar
    with pytest.raises(Exception):
        ViewCommand(
            anime_id=1,
            user_id="user123",
            duration_seconds=-1
        )

