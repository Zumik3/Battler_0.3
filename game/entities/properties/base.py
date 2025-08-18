# game/properties/base.py
"""Базовый класс для свойств, зависящих от статов."""

from abc import ABC
from dataclasses import dataclass
from typing import Optional, Callable
from game.protocols import StatsProtocol


@dataclass
class BaseProperty(ABC):
    pass


@dataclass
class StatsDependentProperty(BaseProperty):
    """Базовый класс для свойств, зависящих от статов персонажа."""
    
    stats: Optional[StatsProtocol] = None
    _subscribed: bool = False
    
    def __post_init__(self) -> None:
        """Инициализация после создания."""
        if self.stats:
            self._recalculate_from_stats(self.stats)
            self._subscribe_to_stats_changes()
    
    def _subscribe_to_stats_changes(self) -> None:
        """Подписывается на изменения статов."""
        if (not self._subscribed and 
            self.stats and 
            hasattr(self.stats, 'add_observer')):
            self.stats.add_observer(self._on_stats_changed)
            self._subscribed = True
    
    def _unsubscribe_from_stats_changes(self) -> None:
        """Отписывается от изменений статов."""
        if (self._subscribed and 
            self.stats and 
            hasattr(self.stats, 'remove_observer')):
            self.stats.remove_observer(self._on_stats_changed)
            self._subscribed = False
    
    def _on_stats_changed(self, stats: StatsProtocol) -> None:
        """Вызывается при изменении статов."""
        self._recalculate_from_stats(stats)
    
    def __del__(self) -> None:
        """Очистка подписок при удалении."""
        self._unsubscribe_from_stats_changes()
    
    def _recalculate_from_stats(self, stats: StatsProtocol) -> None:
        """Пересчитывает свойство на основе статов."""
        raise NotImplementedError