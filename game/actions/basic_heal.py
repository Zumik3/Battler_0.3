# game/actions/heal.py
"""
Модуль реализует действие базового лечения персонажа.
"""

from typing import TYPE_CHECKING

from game.actions.action import Action
from game.events.combat import EnergySpentEvent
from game.events.combat import HealEvent
from game.ui.rendering.render_data_builder import RenderDataBuilder

if TYPE_CHECKING:
    from game.entities.character import Character
    from game.events.render_data import RenderData


class BasicHeal(Action):
    """
    Действие базового лечения.

    Восстанавливает здоровье цели (возможно, только себе или союзникам).
    Взаимодействие происходит через публикацию событий HealEvent.
    """

    def __init__(self, source: 'Character') -> None:
        """
        Инициализирует действие базового лечения.

        Args:
            source: Персонаж, выполняющий лечение.
        """
        super().__init__(source, priority=5) # Приоритет может быть другим, например, ниже, чем у атаки
        self._energy_cost = 10 # Стоимость энергии для выполнения лечения
        self._cooldown = 2 # кулдаун 1 ход (т.е. один кастуем второй ждем потом на 3-й снова кастуем)

    def is_available(self) -> bool:
        """
        Проверяет, доступно ли базовое лечение.

        Returns:
            True если у источника достаточно энергии, иначе False.
        """
        # Проверяем, есть ли у источника свойство энергии и достаточно ли энергии
        return (self.source.energy is not None and 
                self.source.energy.energy >= self.energy_cost)

    def _execute(self) -> None:
        """
        Выполняет базовое лечение через публикацию событий.
        Создает и публикует HealEvent для восстановления здоровья.
        """
        # Можно лечить только себя или союзников, нужно определить логику выбора цели
        if not self.target:
            self.target = self.source

        self._spend_energy()

        # 2. Рассчитываем количество лечения
        heal_amount = self._calculate_heal()

        # 3. Создаем данные для отображения
        render_data = self._create_heal_render_data(
            healer=self.source,
            heal=heal_amount,
            target=self.target
        )
        
        # 4. Создаем и публикуем событие лечения
        heal_event = HealEvent(
            source=None,
            healer=self.source, # Кто лечит
            target=self.target, # Кого лечат
            amount=heal_amount, # Количество восстановленного здоровья
            heal_type="direct", # Тип лечения (прямое, периодическое и т.д.)
            render_data=render_data
        )
        
        self.source.context.event_bus.publish(heal_event)

    def _calculate_heal(self) -> int:
        """
        Рассчитывает количество восстанавливаемого здоровья для базового лечения.

        Returns:
            Рассчитанное значение лечения.
        """
        # Простая формула для примера: базовое значение + часть от интеллекта
        base_heal = 15
        intelligence_bonus = 0
        if hasattr(self.source, 'stats') and self.source.stats:
            # Предполагаем, что у персонажа есть характеристика intelligence
            intelligence_bonus = getattr(self.source.stats, 'intelligence', 0) // 2
        
        heal_amount = base_heal + intelligence_bonus
        return max(1, heal_amount) # Минимальное лечение - 1 HP

    @staticmethod
    def _create_heal_render_data(healer: 'Character', heal: int, target: 'Character') -> 'RenderData':
        """
        Создает данные для отображения события лечения.
        
        Args:
            healer: Персонаж, который лечит.
            heal: Количество восстановленного здоровья.
            target: Персонаж, который получает лечение.
        
        Returns:
            RenderData для отрисовки события.
        """
        return (RenderDataBuilder()
               .add_character_name(healer)
               .add_text(" применяет лечение на ")
               .add_character_name(target)
               .add_text(" и восстанавливает ")
               .add_heal_value(heal)
               .add_text(" здоровья")
               .build())
