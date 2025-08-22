# game/events/reward_events.py
"""Модуль событий, связанных с наградами после боя."""

from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING, Tuple

from game.events.event import Event
# Предотвращаем циклический импорт для типов
if TYPE_CHECKING:
    from game.entities.character import Character
    # Если в будущем будут предметы
    # from game.items.item import Item 


@dataclass
class RewardExperienceGainedEvent(Event['Character']):
    """
    Событие получения опыта персонажем как награды.

    Атрибуты:
        character (Optional[Character]): Персонаж, получивший опыт. Может быть None.
        amount (int): Количество полученного опыта.
        source_level (Optional[int]): Уровень источника опыта (например, уровень побежденного монстра).
    """
    character: Optional['Character'] = None
    amount: int = 0
    source_level: Optional[int] = None
    # Можно добавить информацию об источнике (например, тип монстра)
    # source_type: Optional[str] = None 

    def __post_init__(self):
        """Пост-инициализация для валидации."""
        super().__post_init__()
        if self.amount < 0:
            raise ValueError("Количество опыта не может быть отрицательным.")


# Заглушка для события получения предмета
# В будущем, когда появится система предметов, её можно будет расширить
@dataclass
class ItemLootedEvent(Event['Character']):
    """
    Событие получения предмета персонажем (или группой) как награды.

    Атрибуты:
        character (Optional[Character]): Персонаж, связанный с получением предмета.
                                         Может быть основным получателем или просто участник боя.
        item_name (str): Название полученного предмета (заглушка).
        quantity (int): Количество полученных предметов.
    """
    character: Optional['Character'] = None
    item_name: str = "" # Временная заглушка, инициализируем пустой строкой
    quantity: int = 1

    def __post_init__(self):
        """Пост-инициализация для валидации."""
        super().__post_init__()
        if self.quantity <= 0:
            raise ValueError("Количество предметов должно быть положительным.")
        # if not self.item and not self.item_name:
        #     raise ValueError("Должен быть указан предмет или его название.")


@dataclass
class PartyExperienceGainedEvent(Event[None]):
    """
    Событие получения опыта группой персонажей как награды.

    Атрибуты:
        recipients_and_amounts (List[Tuple[Character, int]]): 
            Список кортежей (персонаж, количество опыта).
        total_experience (int): Общее количество опыта, которое было разделено.
        render_data (Optional[RenderData]): Данные для рендеринга события.
                                            Наследуется от Event, значение по умолчанию None.
    """
    recipients_and_amounts: List[Tuple['Character', int]] = field(default_factory=list)
    total_experience: int = 0

    def __post_init__(self):
        """Пост-инициализация."""
        super().__post_init__()
        if self.total_experience < 0:
            raise ValueError("Общее количество опыта не может быть отрицательным.")

    def __str__(self) -> str:
        """Строковое представление события."""
        if not self.recipients_and_amounts:
            return f"PartyExperienceGainedEvent(Всего опыта: {self.total_experience}, Получатели: нет)"
        parts = [f"{char.name}: {exp}" for char, exp in self.recipients_and_amounts]
        return f"PartyExperienceGainedEvent(Всего опыта: {self.total_experience}, Получатели: {', '.join(parts)})"

# Дополнительные события можно добавлять по аналогии
# @dataclass
# class CurrencyGainedEvent(Event['Character']):
#     """Событие получения валюты."""
#     character: 'Character'
#     amount: int
#     currency_type: str = "золото" # или отдельный enum/класс валют

# @dataclass
# class BuffAppliedEvent(Event['Character']):
#     """Событие применения временного положительного эффекта как награды."""
#     character: 'Character'
#     buff_name: str
#     duration: int # в ходах или секундах
