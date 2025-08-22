# game/rewards/types/experience.py
"""Награда в виде опыта."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from game.rewards.reward import Reward

if TYPE_CHECKING:
    from game.entities.character import Character

@dataclass
class ExperienceReward(Reward):
    """
    Награда в виде опыта.
    
    Атрибуты:
        amount (int): Количество опыта.
        source_level (Optional[int]): Уровень источника опыта (например, монстра).
    """
    amount: int
    source_level: Optional[int] = None

    def __post_init__(self):
        """Пост-инициализация для валидации."""
        if self.amount < 0:
            raise ValueError("Количество опыта не может быть отрицательным.")

    def apply(self, recipient: 'Character') -> None:
        """
        Применяет награду опыта к персонажу.
        Публикует событие ExperienceGainedEvent.
        
        Args:
            recipient (Character): Персонаж, получающий опыт.
        """
        # Публикация события через контекст персонажа
        from game.events.reward_events import ExperienceGainedEvent
        
        event = ExperienceGainedEvent(
            source=recipient, # Источник события - сам получатель или можно None
            character=recipient,
            amount=self.amount,
            source_level=self.source_level
        )
        recipient.context.event_bus.publish(event)

    def __str__(self) -> str:
        level_info = f" (уровень источника: {self.source_level})" if self.source_level else ""
        return f"ExperienceReward({self.amount} XP{level_info})"
