# game/actions/rest.py
"""Модуль реализует действие отдыха."""
from typing import TYPE_CHECKING, Optional

from game.actions.action import Action
from game.events.event import ActionRenderEvent
from game.ui.rendering.color_manager import Color
from game.ui.rendering.render_data_builder import RenderDataBuilder

if TYPE_CHECKING:
    from game.entities.character import Character
    from game.events.render_data import RenderData
    from game.entities.properties.energy import EnergyProperty # Для аннотаций

class Rest(Action):
    """Действие отдыха.
    Восстанавливает 30% от максимальной энергии персонажа.
    Не требует затрат энергии для использования.
    """

    def __init__(self, source: 'Character') -> None:
        """Инициализирует действие отдыха.
        Args:
            source: Персонаж, выполняющий действие.
        """
        # Приоритет низкий, так как это вспомогательное действие
        super().__init__(source, priority=2)
        self._energy_cost = 0  # Не тратит энергию
        self._cooldown = 2     # Пример кулдауна, можно изменить

    @property
    def name(self) -> str:
        """Возвращает имя действия."""
        return "Rest"

    def is_available(self) -> bool:
        """Проверяет, доступно ли действие отдыха.
        Доступно, если персонаж жив и у него есть свойство энергии.
        Можно добавить проверку, что энергия не максимальна, но не обязательно.
        Returns:
            True если действие может быть выполнено, иначе False.
        """
        # Проверяем, жив ли персонаж и есть ли у него энергия
        has_energy_property = self.source.energy is not None
        is_alive = self.source.is_alive() if hasattr(self.source, 'is_alive') else True

        return has_energy_property and is_alive

    def _calculate_energy_restore(self) -> int:
        """Рассчитывает количество восстанавливаемой энергии.
        Returns:
            Количество единиц энергии для восстановления (30% от максимума).
        """
        assert self.source.energy is not None
        max_energy = self.source.energy.max_energy
        restore_amount = int(max_energy * 0.3)
        # Убедимся, что восстанавливается хотя бы 1, если энергия не максимальна
        if restore_amount == 0 and self.source.energy.energy < max_energy:
             restore_amount = 1
        return restore_amount

    def _create_rest_render_data(self, restore_amount: int) -> 'RenderData':
        """Создает данные для отображения восстановления энергии.
        Args:
            restore_amount: Количество восстановленной энергии.
        Returns:
            Объект RenderData.
        """
        return (
            RenderDataBuilder()
            .add_character_name(self.source)
            .add_text(" отдыхает и восстанавливает ")
            .add_styled_text(str(restore_amount), color=Color.BLUE, bold=True)
            .add_text(" энергии.")
            .build()
        )

    def _execute(self) -> None:
        """Выполняет действие отдыха."""
        if not self.source.energy:
            return

        # Рассчитываем количество энергии для восстановления
        restore_amount = self._calculate_energy_restore()

        if restore_amount <= 0:
            return

        self.source.energy.restore_energy(amount=restore_amount)

        # Создаем данные для отображения
        render_data = self._create_rest_render_data(restore_amount)

        render_event = ActionRenderEvent(source=None, render_data=render_data)
        self.source.context.event_bus.publish(render_event)

        if self.source.abilities and hasattr(self.source.abilities, '_cooldown_manager'):
             cooldown_manager = self.source.abilities._cooldown_manager # type: ignore
             if cooldown_manager:
                 cooldown_manager.apply_cooldown(self.source, self.name, self.cooldown)


    def __str__(self) -> str:
        return f"Rest(source={self.source.name})"
