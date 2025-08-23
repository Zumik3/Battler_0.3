"""
Модуль реализует действие базовой атаки персонажа.
"""
from typing import TYPE_CHECKING

from game.actions.action import Action
from game.events.combat import DamageEvent, EnergySpentEvent
from game.systems.combat.damage_type import PHYSICAL
from game.ui.rendering.color_manager import Color
from game.ui.rendering.render_data_builder import RenderDataBuilder
#from game.events.render_data import RenderData

if TYPE_CHECKING:
    from game.entities.character import Character
    from game.events.render_data import RenderData


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

        self._spend_energy()

        # Рассчитываем урон
        damage = self._calculate_damage()
        render_data = self._create_damage_render_data(
            attacker=self.source,
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
    def _create_damage_render_data(attacker: 'Character', damage: int, target: 'Character') -> 'RenderData':
        """
        Создает данные для отображения события нанесения урона.
        
        Args:
            attacker_name: Имя атакующего
            damage: Количество урона
            target_name: Имя цели
        
        Returns:
            RenderData для отрисовки события
        """

        attacker_color = Color.GREEN if attacker.is_player else Color.BLUE
        target_color = Color.GREEN if target.is_player else Color.BLUE

        return (RenderDataBuilder()
               .add_character_name(attacker)
               .add_text(" атакует ")
               .add_character_name(target)
               .add_text(" и наносит ")
               .add_damage_value(damage)
               .add_text(" урона")
               .build())