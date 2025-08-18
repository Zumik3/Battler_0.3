# game/events/__init__.py
"""Система событий игры."""

from .bus import EventBus, Event
from .character import LevelUpEvent, StatsChangedEvent

__all__ = ['EventBus', 'Event', 'LevelUpEvent', 'StatsChangedEvent']