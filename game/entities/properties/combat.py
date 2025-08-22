# game/entities/components/combat.py
"""Свойство боевых показателей персонажа."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Optional, Type

# Импорты из других модулей проекта
from game.entities.properties.base import DependentProperty
from game.events.character import StatsChangedEvent
from game.protocols import CombatPropertyProtocol, StatsProtocol

# Импорты для аннотаций типов
if TYPE_CHECKING:
    from game.events.event import Event # Для аннотации в _on_stats_event

@dataclass
class CombatProperty(DependentProperty, CombatPropertyProtocol):
    """Свойство для управления боевыми показателями персонажа.
    
    Автоматически пересчитывает боевые показатели при изменении связанных статов,
    если был предоставлен объект stats и event_bus через context.
    
    Атрибуты:
        attack_power: Сила атаки персонажа.
        defense: Защита персонажа.
        stats: Ссылка на объект статов, от которых зависит свойство.
               (добавлено, так как DependentProperty его не предоставляет)
        # Атрибуты context, _is_subscribed наследуются от DependentProperty.
    """
    
    attack_power: int = field(default=0)
    defense: int = field(default=0)
    stats: Optional[StatsProtocol] = field(default=None)

    def __post_init__(self) -> None:
        """Инициализация свойства боевых показателей."""
        super().__post_init__()
        if self.stats:
            self._recalculate()
    
    def _setup_subscriptions(self) -> None:
        """Подписывается на изменения статов."""
        if not self._is_subscribed and self.stats and self.context:
            self._subscribe_to(self.stats, StatsChangedEvent, self._on_stats_event)
            self._is_subscribed = True
            print(f"  CombatProperty#{id(self)} подписался на StatsChangedEvent от Stats#{id(self.stats)}")

    def _teardown_subscriptions(self) -> None:
        """Отписывается от изменений статов."""
        if self._is_subscribed and self.stats and self.context:
            self._unsubscribe_from(self.stats, StatsChangedEvent, self._on_stats_event)
            self._is_subscribed = False

    # --- Обработчик события ---
    
    def _on_stats_event(self, event: 'Event') -> None:
        """Вызывается при получении события изменения статов."""
        self._recalculate_from_stats(event.source)
        
    def _recalculate_from_stats(self, stats: StatsProtocol) -> None:
        """Пересчитывает свойство на основе статов."""
        self._recalculate()

    # --- Логика пересчета ---
        
    def _recalculate(self) -> None:
        """Пересчитывает боевые показатели на основе характеристик."""
        if not self.stats:
            self.attack_power = 0
            self.defence = 0
            return
            
        # Формулы пересчета TODO: переписать чтобы пересчитывалось от того что пришло в event
        self.attack_power = getattr(self.stats, 'strength', 0) * 2
        self.defence = getattr(self.stats, 'agility', 0) * 1
