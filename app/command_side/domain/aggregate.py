"""Agregado base."""
from typing import List
from common.events.base_event import BaseEvent


class Aggregate:
    """Clase base para agregados."""
    
    def __init__(self, aggregate_id: str):
        self.aggregate_id = aggregate_id
        self._uncommitted_events: List[BaseEvent] = []
        self._version = 0
    
    def get_uncommitted_events(self) -> List[BaseEvent]:
        """Retorna los eventos no confirmados."""
        return self._uncommitted_events.copy()
    
    def mark_events_as_committed(self):
        """Marca los eventos como confirmados."""
        self._uncommitted_events.clear()
        self._version += len(self._uncommitted_events)
    
    def _add_event(self, event: BaseEvent):
        """Añade un evento a la lista de eventos no confirmados."""
        event.aggregate_id = self.aggregate_id
        event.version = self._version + len(self._uncommitted_events) + 1
        self._uncommitted_events.append(event)

