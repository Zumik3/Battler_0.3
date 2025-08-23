# game/core/context.py
"""Базовый класс контекста для различных компонентов игры."""

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from game.systems.events.bus import IEventBus


class Context:
    """
    Базовый класс для всех контекстов.
    Предоставляет минимальный набор сервисов, необходимых большинству компонентов.
    Может использоваться как есть или наследоваться для расширения функциональности.
    """

    def __init__(self, event_bus: 'IEventBus'):
        """
        Инициализирует базовый контекст.

        Args:
            event_bus: Шина событий игры.
        """
        self._event_bus = event_bus

    @property
    def event_bus(self) -> 'IEventBus':
        """Получить доступ к шине событий."""
        return self._event_bus
