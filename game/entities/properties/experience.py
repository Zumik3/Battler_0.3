# game/entities/properties/experience.py
"""Свойство опыта персонажа."""

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from game.entities.properties.property import PublishingAndDependentProperty 
from game.events.character import ExperienceGainedEvent, LevelUpEvent
from game.protocols import ExperienceSystemProtocol
from game.entities.properties.level import LevelProperty
from game.events.reward_events import RewardExperienceGainedEvent


@dataclass
class ExperienceProperty(PublishingAndDependentProperty, ExperienceSystemProtocol): 
    """Свойство для управления опытом персонажа.
    
    Автоматически публикует событие ExperienceGainedEvent при получении опыта
    и подписывается на события LevelUpEvent для обновления требований опыта.
    
    Атрибуты:
        exp_to_level: Количество опыта, необходимое для следующего уровня.
        current_exp: Текущее количество накопленного опыта.
        level_property: Ссылка на свойство уровня для подписки на его события.
        # Атрибуты context, _is_subscribed наследуются от PublishingAndDependentProperty.
    """
    
    exp_to_level: int = field(default=100) # Пример начального значения
    current_exp: int = field(default=0)
    level_property: Optional['LevelProperty'] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Инициализация свойства опыта."""
        # Вызываем __post_init__ базового класса, который вызовет _setup_subscriptions
        super().__post_init__()
        
        if self.current_exp < 0:
            self.current_exp = 0
    
    def _setup_subscriptions(self) -> None:
        """Подписывается на события повышения уровня."""
        # Проверяем зависимости
        if not self._is_subscribed and self.level_property and self.context and self.context.event_bus:
            self._subscribe_to(self.level_property, LevelUpEvent, self._on_level_up)
            self._subscribe_to(self.context.character,RewardExperienceGainedEvent, self._on_experience_gain)
            self._is_subscribed = True
            
    def _teardown_subscriptions(self) -> None:
        """Отписывается от событий повышения уровня."""
        if self._is_subscribed and self.level_property and self.context and self.context.event_bus:
            self._unsubscribe_from(self.level_property, LevelUpEvent, self._on_level_up)
            self._unsubscribe_from(self.context.character, RewardExperienceGainedEvent, self._on_experience_gain)
            self._is_subscribed = False
            
    # --- Обработчик события ---
    
    def _on_level_up(self, event: LevelUpEvent) -> None:
        """Вызывается при получении события повышения уровня.
        
        Сбрасывает текущий опыт, обрезая то количество, которое "забрало" 
        повышение уровня, и обновляет требование опыта на следующий уровень.
        """  
        # Логика обрезки опыта:
        # 1. Вычисляем, сколько опыта было "потрачено" на уровень.
        #    Это предполагает, что для повышения уровня требовалось ровно exp_to_level опыта.
        # 2. Вычитаем это количество из current_exp.
        # 3. (Опционально) Увеличиваем требование exp_to_level для следующего уровня.
        
        # Пример логики с фиксированным ростом:
        exp_cost_for_previous_level = self.exp_to_level
        self.current_exp -= exp_cost_for_previous_level
        self.current_exp = max(0, self.current_exp) 
        
        self.exp_to_level = int(self.exp_to_level * 1.5) # Увеличиваем на 50%

    def _on_experience_gain(self, event: ExperienceGainedEvent) -> None:
        self.add_experience(event.amount)

    # --- Методы управления опытом ---
    
    def add_experience(self, amount: int) -> None:
        """Добавляет опыт персонажу и публикует событие.
        
        Args:
            amount: Количество опыта для добавления. Должно быть неотрицательным.
        """
        if amount <= 0:
            return # Нет смысла добавлять ноль или отрицательный опыт
            
        self.current_exp += amount
        self._publish_experience_gained()

    def _publish_experience_gained(self) -> None:
        """Создает и публикует событие получения опыта."""
        # Проверяем наличие context и event_bus через context
        if self.context and hasattr(self.context, 'event_bus') and self.context.event_bus:
            event = ExperienceGainedEvent(
                source=self,
                exp_to_level=self.exp_to_level,
                current_exp=self.current_exp
            )
            self._publish(event) # Используем метод из PublisherPropertyMixin

    def get_progress_to_next_level(self) -> float:
        """Получает прогресс до следующего уровня в виде доли (0.0 - 1.0)."""
        if self.exp_to_level <= 0:
            return 0.0 # Избегаем деления на ноль
        return min(1.0, self.current_exp / self.exp_to_level)

    def __str__(self) -> str:
        """Строковое представление опыта."""
        return (f"Experience(current={self.current_exp}, "
                f"to_level={self.exp_to_level}, "
                f"progress={self.get_progress_to_next_level():.2%})")
