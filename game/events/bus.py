# game/events/bus.py
"""Шина событий игры."""

from typing import Dict, List, Callable, Type, TypeVar
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class Event:
    """Базовый класс для всех событий."""
    pass

class EventBus:
    """Шина событий для обмена сообщениями между компонентами."""
    
    def __init__(self):
        self._subscribers: Dict[Type, List[Callable]] = {}
    
    def subscribe(self, event_type: Type[T], callback: Callable[[T], None]):
        """Подписаться на событие определенного типа."""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def publish(self, event: Event):
        """Опубликовать событие."""
        event_type = type(event)
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                callback(event)