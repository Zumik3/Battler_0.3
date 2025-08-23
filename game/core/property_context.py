# game/core/property_context.py
"""Контекст, предоставляемый всем свойствам персонажа."""

from typing import TYPE_CHECKING, Any

from game.core.context import Context

if TYPE_CHECKING:
    from game.entities.character import Character
    from game.systems.events.bus import IEventBus


class PropertyContext(Context):
    """
    Контекст для всех свойств персонажа.
    Наследуется от базового Context и добавляет доступ к персонажу-владельцу.
    """

    def __init__(self, event_bus: 'IEventBus', character: 'Character'):
        """
        Инициализирует контекст свойства.

        Args:
            event_bus: Шина событий игры.
            character: Персонаж, которому принадлежат свойства, использующие этот контекст.
        """
        super().__init__(event_bus=event_bus)
        self._character = character

    @property
    def character(self) -> 'Character':
        """
        Получить доступ к персонажу-владельцу свойств.

        Returns:
            Экземпляр персонажа.
        """
        return self._character
