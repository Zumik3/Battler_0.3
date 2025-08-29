# game/events/__init__.py
"""Система событий игры."""

from .event import Event
from .character import LevelUpEvent, StatsChangedEvent
from .combat import DamageEvent, HealEvent, EnergySpentEvent
from .battle_events import BattleStartedEvent, BattleEndedEvent, RoundStartedEvent, RoundEndedEvent
from .encounter_events import RoomSequenceStartedEvent, RoomCompletedEvent, RoomTransitionEvent, RoomSequenceCompletedEvent

__all__ = [
    'Event',
    'LevelUpEvent', 
    'StatsChangedEvent',
    'DamageEvent',
    'HealEvent',
    'EnergySpentEvent',
    'BattleStartedEvent',
    'BattleEndedEvent',
    'RoundStartedEvent',
    'RoundEndedEvent',
    'RoomSequenceStartedEvent',
    'RoomCompletedEvent',
    'RoomTransitionEvent',
    'RoomSequenceCompletedEvent'
]