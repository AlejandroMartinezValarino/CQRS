from common.exceptions import (
    DomainException,
    AnimeNotFoundError,
    InvalidRatingError
)


def test_domain_exception_base():
    """Test que DomainException es la excepción base."""
    assert issubclass(AnimeNotFoundError, DomainException)
    assert issubclass(InvalidRatingError, DomainException)
    assert issubclass(DomainException, Exception)


def test_anime_not_found_error():
    """Test para AnimeNotFoundError."""
    anime_id = 999
    error = AnimeNotFoundError(anime_id)
    
    assert error.anime_id == anime_id
    assert str(error) == f"Anime con ID {anime_id} no existe"
    assert isinstance(error, DomainException)


def test_anime_not_found_error_custom_message():
    """Test para AnimeNotFoundError con mensaje personalizado."""
    anime_id = 999
    custom_message = "Anime no encontrado en la base de datos"
    error = AnimeNotFoundError(anime_id, message=custom_message)
    
    assert error.anime_id == anime_id
    assert str(error) == custom_message


def test_invalid_rating_error():
    """Test para InvalidRatingError."""
    rating = 11.5
    error = InvalidRatingError(rating)
    
    assert error.rating == rating
    assert str(error) == f"Calificación {rating} no es válida. Debe estar entre 1.0 y 10.0"
    assert isinstance(error, DomainException)


def test_invalid_rating_error_custom_message():
    """Test para InvalidRatingError con mensaje personalizado."""
    rating = 0.5
    custom_message = "Rating debe ser entre 1 y 10"
    error = InvalidRatingError(rating, message=custom_message)
    
    assert error.rating == rating
    assert str(error) == custom_message


def test_invalid_rating_error_boundaries():
    """Test para InvalidRatingError en los límites."""
    error_low = InvalidRatingError(0.9)
    assert error_low.rating == 0.9
    
    error_high = InvalidRatingError(10.1)
    assert error_high.rating == 10.1