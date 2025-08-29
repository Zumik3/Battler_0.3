# game/systems/encounters/__init__.py
"""Система управления походами (энкаунтерами)."""

from .encounter_manager import EncounterManager
from .encounter_generator import EncounterGenerator
from .enemy_factory import EnemyFactory
from .difficulty_scaling import DifficultyScaler
from .room import Room, BattleRoom, TreasureRoom, EmptyRoom, BossRoom
from .room_generator import RoomGenerator
from .room_sequence import RoomSequence, RoomSequenceProgress

__all__ = [
    'EncounterManager',
    'EncounterGenerator',
    'EnemyFactory',
    'DifficultyScaler',
    'Room',
    'BattleRoom',
    'TreasureRoom',
    'EmptyRoom',
    'BossRoom',
    'RoomGenerator',
    'RoomSequence',
    'RoomSequenceProgress'
]