from typing import Optional

class DomainException(Exception):
    """Excepción base del dominio."""
    pass

class AnimeNotFoundError(DomainException):
    """Excepción lanzada cuando un anime no existe."""
    
    def __init__(self, anime_id: int, message: Optional[str] = None):
        self.anime_id = anime_id
        if message is None:
            message = f"Anime con ID {anime_id} no existe"
        super().__init__(message)


class InvalidRatingError(DomainException):
    """Excepción lanzada cuando una calificación es inválida."""
    
    def __init__(self, rating: float, message: Optional[str] = None):
        self.rating = rating
        if message is None:
            message = f"Calificación {rating} no es válida. Debe estar entre 1.0 y 10.0"
        super().__init__(message)