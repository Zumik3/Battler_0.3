# game/entities/components/stats.py
"""Свойство характеристик персонажа."""

from dataclasses import dataclass, field
from typing import Optional
from contextlib import contextmanager

# Импорты из других модулей проекта
from game.entities.properties.base import PublishingAndDependentProperty
from game.events.character import StatsChangedEvent, LevelUpEvent
from game.protocols import StatsProtocol
from game.entities.properties.level import LevelProperty

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
    level_property: Optional['LevelProperty'] = field(default=None, repr=False)
    
    # Атрибуты для пакетного обновления
    _batch_mode: bool = field(default=False, init=False, repr=False)
    _original_values: dict = field(default_factory=dict, init=False, repr=False)
    _has_changes: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        """Инициализация свойства характеристик."""
        super().__post_init__()
    
    def _setup_subscriptions(self) -> None:
        """Подписывается на события повышения уровня."""
        # Проверяем зависимости для подписки
        if not self._is_subscribed and self.level_property and self.context and self.context.event_bus:
            self._subscribe_to(self.level_property, LevelUpEvent, self._on_level_up)
            self._is_subscribed = True
            print(f"  StatsProperty#{id(self)} подписался на LevelUpEvent от Level#{id(self.level_property)}")
            
    def _teardown_subscriptions(self) -> None:
        """Отписывается от событий повышения уровня."""
        if self._is_subscribed and self.level_property and self.context and self.context.event_bus:
            self._unsubscribe_from(self.level_property, LevelUpEvent, self._on_level_up)
            self._is_subscribed = False

    # --- Обработчик события ---
    
    def _on_level_up(self, event: LevelUpEvent) -> None:
        """Вызывается при получении события повышения уровня.
        
        Может быть использован для добавления бонусов к характеристикам.
        В этом примере добавляется небольшой бонус к случайной характеристике.
        """
        # TODO: Переделать на загрузку данных из конфига, 
        # т.к. для разных персонажей уровни поднимаются по разному
        for i in range(abs(event.new_level - event.old_level)):
            self.strength += 1
            self.agility += 1
            self.intelligence +=1
            self.vitality += 1
        # Публикуем событие об изменении, чтобы другие свойства (Health, Energy, Combat) обновились
        # Поскольку это изменение происходит вне стандартных сеттеров,
        # нам нужно вручную вызвать публикацию.
        # В реальном коде это может быть частью более сложной логики.
        self._publish_stats_changed() # Можно вызвать, если нужно немедленное обновление

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

    # --- Модифицированные сеттеры ---
    
    def set_strength(self, value: int) -> None:
        """Устанавливает значение силы."""
        if self.strength != value:
            self.strength = value
            self._mark_changed()

    def set_agility(self, value: int) -> None:
        """Устанавливает значение ловкости."""
        if self.agility != value:
            self.agility = value
            self._mark_changed()

    def set_intelligence(self, value: int) -> None:
        """Устанавливает значение интеллекта."""
        if self.intelligence != value:
            self.intelligence = value
            self._mark_changed()

    def set_vitality(self, value: int) -> None:
        """Устанавливает значение выносливости."""
        if self.vitality != value:
            self.vitality = value
            self._mark_changed()

    def modify_strength(self, delta: int) -> None:
        """Изменяет значение силы на delta."""
        new_value = self.strength + delta
        if self.strength != new_value:
            self.strength = new_value
            self._mark_changed()

    def modify_agility(self, delta: int) -> None:
        """Изменяет значение ловкости на delta."""
        new_value = self.agility + delta
        if self.agility != new_value:
            self.agility = new_value
            self._mark_changed()

    def modify_intelligence(self, delta: int) -> None:
        """Изменяет значение интеллекта на delta."""
        new_value = self.intelligence + delta
        if self.intelligence != new_value:
            self.intelligence = new_value
            self._mark_changed()

    def modify_vitality(self, delta: int) -> None:
        """Изменяет значение выносливости на delta."""
        new_value = self.vitality + delta
        if self.vitality != new_value:
            self.vitality = new_value
            self._mark_changed()
            
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

    # --- Вспомогательные методы ---
    
    def get_stat(self, stat_name: str) -> Optional[int]:
        """Получает значение характеристики по имени."""
        return getattr(self, stat_name, None)

    def __str__(self) -> str:
        """Строковое представление характеристик."""
        return (f"Stats(strength={self.strength}, agility={self.agility}, "
                f"intelligence={self.intelligence}, vitality={self.vitality})")
