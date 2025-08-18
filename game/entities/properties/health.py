# game/entities/components/health.py
"""Свойство здоровья персонажа."""

from dataclasses import dataclass
from typing import List
from game.entities.properties.base import StatsDependentProperty
from game.protocols import HealthPropertyProtocol, StatsProtocol
from game.results import ActionResult, DamageTakenResult, HealedResult

@dataclass
class HealthProperty(StatsDependentProperty, HealthPropertyProtocol):
    """Свойство для управления здоровьем персонажа."""
    
    max_health: int = 0
    health: int = 0
    
    def _recalculate_from_stats(self, stats: StatsProtocol) -> None:
        """Пересчитывает HP на основе vitality."""
        base_hp = 100
        hp_per_vitality = 10
        self.max_health = base_hp + (stats.vitality * hp_per_vitality)
        
        # Если текущее HP больше нового максимума - уменьшаем
        if self.health > self.max_health:
            self.health = self.max_health


    def take_damage(self, damage: int, defense: int = 0) -> List[ActionResult]:
        """Наносит урон, учитывая защиту."""
        results: List[ActionResult] = []
        
        actual_damage = max(0, damage - defense // 2)
        actual_damage = max(1, actual_damage) if damage > 0 else 0

        self.health -= actual_damage
        results.append(DamageTakenResult(
            target="",  # Будет заполнен позже
            damage=actual_damage,
            hp_left=self.health
        ))
        
        return results
    
    def take_heal(self, heal_amount: int) -> List[ActionResult]:
        """Исцеляет персонажа."""
        results: List[ActionResult] = []
        old_hp = self.health
        self.health = min(self.max_health, self.health + heal_amount)
        actual_heal = self.health - old_hp
        results.append(HealedResult(
            target="",  # Будет заполнен позже
            heal_amount=actual_heal,
            hp_now=self.health
        ))
        return results
    
    def is_alive(self) -> bool:
        """Проверяет, жив ли персонаж."""
        return self.health > 0
    
    def restore_full_health(self) -> None:
        """Полностью восстанавливает здоровье."""
        self.health = self.max_health