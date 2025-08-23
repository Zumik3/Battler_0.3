# game/events/event.py
"""Базовый класс для всех событий."""

from datetime import datetime
import sys
from typing import TYPE_CHECKING, Generic, Optional, TypeVar
from dataclasses import dataclass, field
import uuid

from game.events import render_data

if TYPE_CHECKING:
    from game.events.render_data import RenderData

T = TypeVar('T', bound='Event')
TSource = TypeVar('TSource')


@dataclass
class Event(Generic[TSource]):
    """Базовый класс для всех событий с указанием источника.

    Атрибуты:
        source: Объект, который инициировал событие.
    """
    source: TSource
    """Объект, который инициировал событие."""
    # Метаданные для аналитики и логирования
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    battle_id: Optional[str] = None  # Для группировки событий одного боя
    session_id: Optional[str] = None  # Для группировки событий сессии

    render_data: Optional['RenderData'] = None
    
    def __post_init__(self):
        """Валидация базовых полей."""
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
