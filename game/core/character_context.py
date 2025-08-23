# game/core/character_context.py
"""Контекст, предоставляемый компонентам, связанным с конкретным персонажем."""

from typing import TYPE_CHECKING, Dict

from game.core.context import Context

if TYPE_CHECKING:
    from game.entities.character import Character
    from game.systems.events.bus import IEventBus


class CharacterContext(Context):
    """
    Контекст для компонентов, связанных с конкретным персонажем.
    Наследуется от базового Context и добавляет доступ к самому персонажу,
    его базовым характеристикам и коэффициентам роста.
    """

    def __init__(
        self, 
        event_bus: 'IEventBus', 
        #base_stats: Dict[str, int],
        #growth_rates: Dict[str, float]
    ):
        """
        Инициализирует контекст персонажа.

        Args:
            event_bus: Шина событий игры.
            character: Персонаж, к которому относится этот контекст.
            base_stats: Базовые значения характеристик персонажа на 1 уровне.
            growth_rates: Коэффициенты роста характеристик персонажа.
        """
        super().__init__(event_bus=event_bus)

    @property
    def base_stats(self) -> Dict[str, int]:
        """Получить базовые значения характеристик персонажа."""
        return self._base_stats

    @property
    def growth_rates(self) -> Dict[str, float]:
        """Получить коэффициенты роста характеристик персонажа."""
        return self._growth_rates

    def set_base_characteristics(self, base_stats: Dict[str, int], 
        growth_rates: Dict[str, float]) -> None:

        self._base_stats = base_stats
        self._growth_rates = growth_rates

