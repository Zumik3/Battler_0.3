# game/events/reward_events.py
"""Модуль событий, связанных с наградами после боя."""

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

# Предотвращаем циклический импорт для типов
if TYPE_CHECKING:
    from game.entities.character import Character
    # Если в будущем будут предметы
    # from game.items.item import Item 

from game.events.event import Event
from game.events.render_data import RenderData


@dataclass
class ExperienceGainedEvent(Event['Character']):
    """
    Событие получения опыта персонажем.
    
    Атрибуты:
        character (Character): Персонаж, получивший опыт.
        amount (int): Количество полученного опыта.
        source_level (Optional[int]): Уровень источника опыта (например, уровень побежденного монстра).
    """
    character: 'Character'
    amount: int
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
    Событие получения предмета персонажем (или группой).
    
    Атрибуты:
        character (Character): Персонаж, связанный с получением предмета
                               (может быть основным получателем или просто участник боя).
        # item (Item): Полученный предмет.
        item_name (str): Название полученного предмета (заглушка).
        quantity (int): Количество полученных предметов.
    """
    character: 'Character'
    # item: 'Item' # Потребуется импорт из модуля предметов
    item_name: str # Временная заглушка
    quantity: int = 1

    def __post_init__(self):
        """Пост-инициализация для валидации."""
        super().__post_init__()
        if self.quantity <= 0:
            raise ValueError("Количество предметов должно быть положительным.")
        # if not self.item and not self.item_name:
        #     raise ValueError("Должен быть указан предмет или его название.")

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