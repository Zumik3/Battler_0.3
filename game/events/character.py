# game/events/character.py
"""События, связанные с персонажами."""

from dataclasses import dataclass
from typing import Any
from game.events.event import Event

@dataclass
class LevelUpEvent(Event):
    """Событие повышения уровня персонажа."""
    old_level: int = 0
    new_level: int = 0


@dataclass
class ExperienceGainedEvent(Event):
    """Событие получения опыта персонажем."""
    amount: int = 0
    current_exp: int = 0
    exp_to_level: int = 100


@dataclass
class StatsChangedEvent(Event):
    """Событие изменения характеристик персонажа."""
    changed: bool = True

@dataclass
class HealthChangedEvent(Event):
    """Событие изменения здоровья персонажа."""
    new_health: int = 0

@dataclass
class EnergyChangedEvent(Event):
    """Событие изменения энергии персонажа."""
    character: Any = None
    old_energy: int = 0
    new_energy: int = 0
    max_energy: int = 0