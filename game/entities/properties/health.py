# game/entities/properties/health.py
"""Свойство здоровья персонажа."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from game.events.combat import DamageEvent, HealEvent
from game.protocols import HealthPropertyProtocol, StatsProtocol
from game.entities.properties.property import PublishingAndDependentProperty
from game.events.character import HealthChangedEvent, StatsChangedEvent
from game.systems.events.bus import LOW_PRIORITY

if TYPE_CHECKING:
    from game.core.game_context import GameContext


@dataclass
class HealthProperty(PublishingAndDependentProperty, HealthPropertyProtocol):
    """Свойство для управления здоровьем персонажа.
    
    Автоматически пересчитывает максимальное здоровье при изменении статов,
    если были предоставлены объекты stats и event_bus.
    
    Атрибуты:
        max_health: Максимальный запас здоровья.
        health: Текущий запас здоровья.
        stats: Ссылка на объект статов, от которых зависит свойство.
               (добавлено, так как DependentProperty его не предоставляет)
        # Атрибуты event_bus, _is_subscribed наследуются от DependentProperty.
    """
    
    BASE_HEALTH: int = field(default=100, init=False, repr=False)
    HEALTH_PER_VITALITY: int = field(default=10, init=False, repr=False)

    max_health: int = field(default=0)
    health: int = field(default=0)
    stats: Optional[StatsProtocol] = field(default=None)

    def __post_init__(self) -> None:
        """Инициализация свойства здоровья."""
        super().__post_init__()
        
        if self.stats and self.max_health == 0:
            self._recalculate()
            if self.health == 0: 
                self.health = self.max_health
    
    def _setup_subscriptions(self) -> None:
        """Подписывается на изменения статов."""
        # Проверяем, не подписаны ли мы уже и существуют ли необходимые зависимости
        if not self._is_subscribed and self.stats and self.context:
            self._subscribe_to(self.stats, StatsChangedEvent, self._on_stats_event)
            self._subscribe_to(None, DamageEvent, self._on_damage_event, LOW_PRIORITY)
            self._subscribe_to(None, HealEvent, self._on_heal_event, LOW_PRIORITY)
            self._is_subscribed = True
            
    def _on_stats_event(self, event: StatsChangedEvent) -> None:
        """Вызывается при получении события изменения статов."""
        self._recalculate()

    def _on_damage_event(self, event: DamageEvent) -> None:
        """Вызывается при получении события получения урона."""
        # Защитное программирование: проверяем, жив ли персонаж перед применением урона
        if self.context.character is event.target and event.target.is_alive():
            self.take_damage(event.amount)

    def _on_heal_event(self, event: DamageEvent) -> None:
        """Вызывается при получении события получения урона."""
        # Защитное программирование: проверяем, жив ли персонаж перед применением урона
        if self.context.character is event.target and event.target.is_alive():
            self.take_heal(event.amount)
        
    def _recalculate(self) -> None:
        """Пересчитывает максимальное HP на основе vitality."""
        
        if not self.stats:
            # Если по какой-то причине stats нет, устанавливаем базовые значения
            self.max_health = self.BASE_HEALTH
            if self.health > self.max_health or self.health == 0:
                self.health = self.max_health
            return
            
        # Логика пересчета на основе статов
        new_max_health = self.BASE_HEALTH + (getattr(self.stats, 'vitality', 0) * self.HEALTH_PER_VITALITY)
        self.max_health = new_max_health
        
        self.restore_full_health()

    # --- Методы управления здоровьем ---
    
    def take_damage(self, damage: int, defense: int = 0) -> None:
        """Наносит урон, учитывая защиту."""
        actual_damage = max(0, damage - defense // 2)
        actual_damage = max(1, actual_damage) if damage > 0 else 0

        self.health -= actual_damage
        # Убеждаемся, что здоровье не уйдет в минус
        self.health = max(0, self.health)
        self._publish_health_changed()

    def take_heal(self, heal_amount: int) -> None:
        """Исцеляет персонажа."""
        old_hp = self.health
        self.health = min(self.max_health, self.health + heal_amount)
        # actual_heal = self.health - old_hp # Переменная удалена, так как не используется
        self._publish_health_changed()
    
    def is_alive(self) -> bool:
        """Проверяет, жив ли персонаж."""
        return self.health > 0
    
    def restore_full_health(self) -> None:
        """Полностью восстанавливает здоровье."""
        self.health = self.max_health
        self._publish_health_changed()

    def _publish_health_changed(self) -> None:
        """Создает и публикует событие HealthChangedEvent."""
        if self.context and hasattr(self.context, 'event_bus') and self.context.event_bus:
            event = HealthChangedEvent(source=self, new_health=self.health)
            self._publish(event)
