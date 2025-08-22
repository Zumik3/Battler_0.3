# game/rewards/reward.py
"""Абстрактный базовый класс для всех наград."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.entities.character import Character

class Reward(ABC):
    """
    Абстрактный базовый класс для всех наград.
    
    Все конкретные типы наград должны наследоваться от этого класса
    и реализовывать метод `apply`.
    """

    @abstractmethod
    def apply(self, recipient: 'Character') -> None:
        """
        Применяет награду к указанному персонажу.
        
        Args:
            recipient (Character): Персонаж, получающий награду.
        """
        pass

    # Можно добавить метод __str__ или другие общие методы, если нужно
    # def __str__(self) -> str:
    #     return f"{self.__class__.__name__}()"