# game/events/character.py
"""События, связанные с персонажами."""

from dataclasses import dataclass
from .bus import Event

@dataclass
class LevelUpEvent(Event):
    """Событие повышения уровня персонажа."""
    character_name: str
    old_level: int
    new_level: int

@dataclass
class StatsChangedEvent(Event):
    """Событие изменения характеристик персонажа."""
    character_name: str
    strength: int
    agility: int
    intelligence: int
    vitality: int

@dataclass
class HealthChangedEvent(Event):
    """Событие изменения здоровья персонажа."""
    character_name: str
    old_health: int
    new_health: int
    max_health: int

@dataclass
class EnergyChangedEvent(Event):
    """Событие изменения энергии персонажа."""
    character_name: str
    old_energy: int
    new_energy: int
    max_energy: int