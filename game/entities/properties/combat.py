# game/entities/components/combat.py
"""Свойство боевых показателей персонажа."""

from dataclasses import dataclass
from typing import List, Optional
from game.entities.properties.base import StatsDependentProperty
from game.protocols import CombatPropertyProtocol, StatsProtocol
from game.results import ActionResult, DamageTakenResult, HealedResult

@dataclass
class CombatProperty(StatsDependentProperty, CombatPropertyProtocol):
    """Свойство для управления боевыми показателями персонажа."""
    
    attack_power: int = 0
    defence: int = 0

    def __post_init__(self):
        super().__post_init__()

    def _recalculate_from_stats(self, stats: StatsProtocol) -> None:
        """Пересчитывает боевые показатели на основе характеристик."""
        self.attack_power = getattr(stats, 'strength', 0) * 2
        self.defence = getattr(stats, 'agility', 0) * 1
