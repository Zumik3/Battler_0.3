"""
Модуль реализует действие базовой атаки персонажа.
"""
from typing import TYPE_CHECKING

from game.actions.action import Action
from game.events.combat import DamageEvent, EnergySpentEvent
from game.events.render_data import RenderData
from game.systems.damage.damage_type import PHYSICAL
from game.ui.rendering.color_manager import Color

if TYPE_CHECKING:
    from game.entities.character import Character


class BasicAttack(Action):
    """
    Действие базовой физической атаки.

    Наносит урон цели на основе атаки источника и защиты цели.
    Взаимодействие происходит через публикацию событий DamageEvent.
    """

    def __init__(self, source: 'Character') -> None:
        """
        Инициализирует действие базовой атаки.

        Args:
            source: Персонаж, выполняющий атаку.
        """
        super().__init__(source, priority=10)
        self._energy_cost = 5

    @property
    def name(self) -> str:
        """Возвращает название действия."""
        return type(self).__name__

    @property
    def energy_cost(self) -> int:
        """Возвращает стоимость энергии для выполнения действия."""
        return self._energy_cost

    @energy_cost.setter
    def energy_cost(self, value: int) -> None:
        """Устанавливает стоимость энергии."""
        self._energy_cost = value

    def is_available(self) -> bool:
        """
        Проверяет, доступна ли базовая атака.

        Returns:
            True если у источника достаточно энергии, иначе False.
        """
        return self.source.energy is not None and self.source.energy.energy >= self.energy_cost

    def _execute(self) -> None:
        """
        Выполняет базовую араку через публикацию событий.
        Создает и публикует DamageEvent для нанесения урона.
        """
        if not self.target:
            return

        # 1. Публикуем событие траты энергии
        energy_event = EnergySpentEvent(
            source=None,
            character=self.source,
            amount=self.energy_cost,
            reason=f"action_{self.name}"
        )
        self.source.context.event_bus.publish(energy_event)


        # Рассчитываем урон
        damage = self._calculate_damage()
        render_data = self._create_damage_render_data(
            atacker=self.source,
            damage=damage,
            target=self.target)
        
        # Создаем и публикуем событие нанесения урона
        damage_event = DamageEvent(
            source=None,
            attacker=self.source,
            target=self.target,
            amount=damage,
            damage_type=PHYSICAL,
            is_critical=False,
            can_be_blocked=True,
            render_data=render_data
        )
        
        self.source.context.event_bus.publish(damage_event)

    def _calculate_damage(self) -> int:
        """
        Рассчитывает количество урона для базовой атаки.

        Returns:
            Рассчитанное значение урона.
        """
        if not (self.source.combat and self.target and self.target.combat):
            return 0
            
        attack_power = self.source.combat.attack_power
        target_defense = self.target.combat.defense
        damage = max(1, attack_power - target_defense // 2)
        
        return damage

    @staticmethod
    def _create_damage_render_data(atacker: 'Character', damage: int, target: 'Character') -> RenderData:
        """
        Создает данные для отображения события нанесения урона.
        
        Args:
            attacker_name: Имя атакующего
            damage: Количество урона
            target_name: Имя цели
        
        Returns:
            RenderData для отрисовки события
        """

        atacker_color = Color.GREEN if atacker.is_player else Color.BLUE
        target_color = Color.GREEN if target.is_player else Color.BLUE

        return RenderData(
            template="%1 атакует %2 и наносит %3 урона",
            replacements={
                "1": (atacker.name, atacker_color, True, False),
                "2": (target.name, target_color, False, False),
                "3": (f"{damage}", Color.RED, True, False)
            }
        )