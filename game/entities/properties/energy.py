# game/entities/components/energy.py
"""Свойство энергии персонажа."""

from dataclasses import dataclass
from typing import List, Optional
from game.entities.properties.base import StatsDependentProperty
from game.protocols import EnergyPropertyProtocol, StatsProtocol
from game.results import ActionResult

@dataclass
class EnergyProperty(StatsDependentProperty, EnergyPropertyProtocol):
    """Свойство для управления энергией персонажа."""
    
    max_energy: int = 0
    energy: int = 0
    
    def __post_init__(self):
        super().__post_init__()
    
    def _recalculate_from_stats(self, stats: StatsProtocol) -> None:
        """Пересчитывает энергию на основе intelligence."""
        base_energy = 100
        energy_per_intelligence = 10
        self.max_energy = base_energy + (stats.intelligence * energy_per_intelligence)
        
        if self.energy > self.max_energy:
            self.energy = self.max_energy

    def restore_energy(self, amount: Optional[int] = None, 
                      percentage: Optional[float] = None) -> List[ActionResult]:
        """Восстанавливает энергию персонажа."""
        results: List[ActionResult] = []
        old_energy = self.energy

        if percentage is not None:
            restore_amount = int(self.max_energy * (percentage / 100.0))
            self.energy = min(self.max_energy, self.energy + restore_amount)
        elif amount is not None:
            self.energy = min(self.max_energy, self.energy + amount)
        else:
            self.energy = self.max_energy

        actual_restore = self.energy - old_energy
        if actual_restore > 0:
            results.append(ActionResult(
                type="energy_restored",
                message=f"Восстановлено {actual_restore} энергии. Текущая энергия: {self.energy}"
            ))

        return results
    
    def spend_energy(self, amount: int) -> bool:
        """Тратит энергию персонажа."""
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False
    
    def restore_full_energy(self) -> None:
        """Полностью восстанавливает энергию."""
        self.energy = self.max_energy