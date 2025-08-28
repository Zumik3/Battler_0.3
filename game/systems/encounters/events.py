# game/systems/encounters/events.py
"""Модуль, определяющий события, которые могут произойти во время похода."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from game.game_manager import GameManager

class EncounterEvent(ABC):
    """Абстрактный базовый класс для всех событий в походе."""

    @abstractmethod
    def execute(self, game_manager: 'GameManager') -> None:
        """
        Выполняет логику события.

        Args:
            game_manager: Менеджер игры для доступа к игровым системам.
        """
        pass

@dataclass
class BattleEncounterEvent(EncounterEvent):
    """
    Событие, представляющее собой бой с группой врагов.

    Атрибуты:
        enemies (List[Dict[str, Any]]): Список словарей, описывающих врагов.
                                       Каждый словарь должен содержать 'role' и 'level'.
    """
    enemies: List[Dict[str, Any]]

    def execute(self, game_manager: 'GameManager') -> None:
        """
        Создает врагов и инициирует бой.
        """
        # В будущем здесь может быть более сложная логика,
        # например, передача специфичного для боя контекста.
        game_manager.create_enemies(self.enemies, game_manager.context)
        game_manager.start_battle()