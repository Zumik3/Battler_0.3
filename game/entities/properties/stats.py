# game/entities/components/stats.py
"""Свойство характеристик персонажа."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional
from contextlib import contextmanager

from game.protocols import StatsProtocol
from game.events.character import StatsChangedEvent, LevelUpEvent
from game.entities.properties.base import PublishingAndDependentProperty

if TYPE_CHECKING:
    from game.protocols import LevelPropertyProtocol, StatsConfigurable


@dataclass
class StatsProperty(PublishingAndDependentProperty, StatsProtocol):
    """Свойство для хранения и управления базовыми характеристиками персонажа.
    
    Публикует событие StatsChangedEvent после изменения характеристик.
    Подписывается на события LevelUpEvent для потенциальной модификации характеристик
    при повышении уровня (например, добавление бонусов).
    
    Атрибуты:
        strength: Сила персонажа.
        agility: Ловкость персонажа.
        intelligence: Интеллект персонажа.
        vitality: Выносливость персонажа.
        level_property: Ссылка на свойство уровня для подписки на его события.
                       (добавлено, так как PublishingAndDependentProperty не предоставляет его)
        _batch_mode: Флаг, указывающий, находится ли свойство в режиме пакетного обновления.
        _original_values: Словарь для хранения оригинальных значений во время пакетного обновления.
        _has_changes: Флаг, указывающий, были ли изменения во время пакетного обновления.
        # Атрибуты context, _is_subscribed наследуются.
    """
    # Атрибуты характеристик
    strength: int = field(default=10)
    agility: int = field(default=10)
    intelligence: int = field(default=10)
    vitality: int = field(default=10)
    
    # Добавляем ссылку на LevelProperty для подписки
    level_source: Optional['LevelPropertyProtocol'] = field(default=None, repr=False)
    stats_config: Optional['StatsConfigurable'] = field(default=None, repr=False)
    
    # Атрибуты для пакетного обновления
    _batch_mode: bool = field(default=False, init=False, repr=False)
    _original_values: dict = field(default_factory=dict, init=False, repr=False)
    _has_changes: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        """Инициализация свойства характеристик."""
        super().__post_init__()
        
        if self.stats_config:
            base_stats = self.stats_config.get_base_stats()
            for attr_name, value in base_stats.items():
                setattr(self, attr_name, value)
    
    def _setup_subscriptions(self) -> None:
        """Подписывается на события повышения уровня."""
        # Проверяем зависимости для подписки
        if not self._is_subscribed and self.level_source and self.context and self.context.event_bus:
            self._subscribe_to(self.level_source, LevelUpEvent, self._on_level_up)
            self._is_subscribed = True
            
    # --- Обработчик события ---
    
    def _on_level_up(self, event: LevelUpEvent) -> None:
        """Вызывается при получении события повышения уровня."""
        if self.stats_config:
            new_stats = self.stats_config.calculate_all_stats_at_level(event.new_level)
    
            with self.batch_update():
                for stat_name, value in new_stats.items():
                    setattr(self, stat_name, value)
    

    # --- Методы для пакетного обновления ---
    
    def start_batch_update(self) -> None:
        """Начинает пакетное обновление. Сохраняет оригинальные значения."""
        if not self._batch_mode:
            self._batch_mode = True
            self._has_changes = False
            # Сохраняем копию текущих значений
            self._original_values = {
                'strength': self.strength,
                'agility': self.agility,
                'intelligence': self.intelligence,
                'vitality': self.vitality,
            }
        # Если уже в batch_mode, просто продолжаем (для вложенных вызовов)

    def end_batch_update(self) -> None:
        """Завершает пакетное обновление и публикует событие, если были изменения."""
        if self._batch_mode:
            self._batch_mode = False
            # Проверяем, были ли фактические изменения
            if self._has_changes or self._check_for_changes():
                self._publish_stats_changed()
            # Очищаем временное состояние
            self._original_values.clear()
            self._has_changes = False
            
    def _check_for_changes(self) -> bool:
        """Проверяет, были ли фактические изменения значений."""
        return (
            self.strength != self._original_values.get('strength', self.strength) or
            self.agility != self._original_values.get('agility', self.agility) or
            self.intelligence != self._original_values.get('intelligence', self.intelligence) or
            self.vitality != self._original_values.get('vitality', self.vitality)
        )

    @contextmanager
    def batch_update(self):
        """Контекстный менеджер для удобного пакетного обновления."""
        self.start_batch_update()
        try:
            yield self
        finally:
            self.end_batch_update()
            
    def _mark_changed(self) -> None:
        """Помечает, что были изменения. Публикует событие, если не в batch_mode."""
        if self._batch_mode:
            # В пакетном режиме просто отмечаем, что были изменения
            self._has_changes = True
        else:
            # Если не в пакетном режиме, публикуем сразу
            self._publish_stats_changed()

    def _publish_stats_changed(self) -> None:
        """Создает и публикует событие StatsChangedEvent."""
        if self.context and hasattr(self.context, 'event_bus') and self.context.event_bus:
            event = StatsChangedEvent(source=self)
            self._publish(event)
