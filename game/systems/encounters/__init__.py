# game/systems/encounters/__init__.py
"""Система управления походами (энкаунтерами)."""

from .encounter_manager import EncounterManager
from .encounter_generator import EncounterGenerator
from .enemy_factory import EnemyFactory
from .difficulty_scaling import DifficultyScaler

__all__ = [
    'EncounterManager',
    'EncounterGenerator',
    'EnemyFactory',
    'DifficultyScaler'
]