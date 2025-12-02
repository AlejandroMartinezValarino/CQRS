"""Manejador de comandos base."""
from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from common.dto.command_dto import ClickCommand, ViewCommand, RatingCommand

TCommand = TypeVar("TCommand")


class CommandHandler(ABC, Generic[TCommand]):
    """Interfaz base para manejadores de comandos."""
    
    @abstractmethod
    async def handle(self, command: TCommand) -> None:
        """Maneja un comando."""
        pass

