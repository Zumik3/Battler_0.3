# game/actions/basic_attack_action.py
"""
Модуль реализует действие базовой атаки персонажа.
"""
from typing import List, TYPE_CHECKING

from game.actions.action import Action
from game.results import ActionResult, DamageTakenResult

if TYPE_CHECKING:
    from game.entities.character import Character


class BasicAttack(Action):
    """
    Действие базовой физической атаки.

    Наносит урон цели based on атаки источника и защиты цели.
    """

    def __init__(self, source: 'Character') -> None:
        """
        Инициализирует действие базовой атаки.

        Args:
            source: Персонаж, выполняющий атаку.
        """
        super().__init__(source, priority=10)
        self.energy_cost = 1

    @property
    def name(self) -> str:
        return "Базовая атака"

    @property
    def energy_cost(self) -> int:
        return self._energy_cost

    @energy_cost.setter
    def energy_cost(self, value: int) -> None:
        self._energy_cost = value

    def is_available(self) -> bool:
        """
        Проверяет, доступна ли базовая атака.

        Returns:
            True если у источника достаточно энергии, иначе False.
        """
        if self.source.energy:
            return self.source.energy.get() >= self.energy_cost
        else:
            return False

    def _execute(self) -> List[ActionResult]:
        """
        Выполняет базовую атаку.

        Returns:
            Список результатов атаки, включая нанесенный урон.
        """
        results: List[ActionResult] = []
        if self.target is None:
            return results
        
        # Расходуем энергию
        if self.source.energy:
            energy_spent = self.source.energy.spend_energy(self.energy_cost)
            if energy_spent != 0:
                results.append(ActionResult(
                    type="energy_spent",
                    message=f"{self.source.name} тратит {abs(energy_spent)} энергии."
                ))

        # Рассчитываем урон
        if self.source.combat and self.target.health and self.target.combat:
            attack_power = self.source.combat.attack_power
            target_defense = self.target.combat.defense if self.target else 0
            damage = max(1, attack_power - target_defense // 2)

            # Наносим урон цели
            damage_results = self.target.health.take_damage(damage)
            results.extend(damage_results)

            # Добавляем сообщение об атаке
            results.append(ActionResult(
                type="attack_performed",
                message=f"{self.source.name} атакует {self.target.name}!"
            ))

        return results