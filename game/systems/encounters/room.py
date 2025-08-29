# game/systems/encounters/room.py
"""Базовые классы для комнат в encounter'ах."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.entities.monster import Monster


class RoomType(Enum):
    """Типы комнат."""
    BATTLE = "battle"
    TREASURE = "treasure"
    EMPTY = "empty"
    BOSS = "boss"


class RoomStatus(Enum):
    """Статус комнаты."""
    UNVISITED = "unvisited"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class Room(ABC):
    """Базовый абстрактный класс для комнат."""

    def __init__(self, room_type: RoomType, position: int, total_rooms: int):
        """
        Инициализирует комнату.
        
        Args:
            room_type: Тип комнаты
            position: Позиция комнаты в последовательности (0-indexed)
            total_rooms: Общее количество комнат в последовательности
        """
        self.room_type = room_type
        self.position = position
        self.total_rooms = total_rooms
        self.status = RoomStatus.UNVISITED
        self.description = ""

    @abstractmethod
    def enter(self) -> Dict[str, Any]:
        """
        Вызывается при входе в комнату.
        
        Returns:
            Словарь с данными для обработки комнаты
        """
        pass

    def complete(self) -> None:
        """Помечает комнату как пройденную."""
        self.status = RoomStatus.COMPLETED

    def fail(self) -> None:
        """Помечает комнату как проваленную."""
        self.status = RoomStatus.FAILED

    def activate(self) -> None:
        """Активирует комнату."""
        self.status = RoomStatus.ACTIVE

    def is_boss_room(self) -> bool:
        """Проверяет, является ли комната боссовой."""
        return self.position == self.total_rooms - 1

    def get_progress_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о прогрессе комнаты.
        
        Returns:
            Словарь с информацией о прогрессе
        """
        return {
            "position": self.position,
            "total_rooms": self.total_rooms,
            "status": self.status.value,
            "is_boss": self.is_boss_room()
        }


class BattleRoom(Room):
    """Комната с боем."""

    def __init__(self, position: int, total_rooms: int, enemies: List[Dict[str, Any]]):
        """
        Инициализирует боевую комнату.
        
        Args:
            position: Позиция комнаты в последовательности
            total_rooms: Общее количество комнат
            enemies: Список врагов в формате [{'role': str, 'level': int}, ...]
        """
        super().__init__(RoomType.BATTLE, position, total_rooms)
        self.enemies = enemies
        self.description = self._generate_description()

    def enter(self) -> Dict[str, Any]:
        """
        Вызывается при входе в боевую комнату.
        
        Returns:
            Словарь с данными о врагах
        """
        return {
            "type": "battle",
            "enemies": self.enemies
        }

    def _generate_description(self) -> str:
        """Генерирует описание боевой комнаты."""
        if self.is_boss_room():
            return "Вы чувствуете мощную энергию. Похоже, это финальный бой!"
        elif self.position == 0:
            return "Первый бой в этом месте. Враги готовы к сражению."
        else:
            return "Еще один бой. Враги преграждают путь дальше."


class TreasureRoom(Room):
    """Комната с сокровищами."""

    def __init__(self, position: int, total_rooms: int, rewards: List[Dict[str, Any]]):
        """
        Инициализирует комнату с сокровищами.
        
        Args:
            position: Позиция комнаты в последовательности
            total_rooms: Общее количество комнат
            rewards: Список наград
        """
        super().__init__(RoomType.TREASURE, position, total_rooms)
        self.rewards = rewards
        self.description = "Вы нашли комнату с сокровищами!"

    def enter(self) -> Dict[str, Any]:
        """
        Вызывается при входе в комнату с сокровищами.
        
        Returns:
            Словарь с данными о наградах
        """
        return {
            "type": "treasure",
            "rewards": self.rewards
        }


class EmptyRoom(Room):
    """Пустая комната."""

    def __init__(self, position: int, total_rooms: int):
        """
        Инициализирует пустую комнату.
        
        Args:
            position: Позиция комнаты в последовательности
            total_rooms: Общее количество комнат
        """
        super().__init__(RoomType.EMPTY, position, total_rooms)
        self.description = "Пустая комната. Можно немного отдохнуть."

    def enter(self) -> Dict[str, Any]:
        """
        Вызывается при входе в пустую комнату.
        
        Returns:
            Словарь с данными о пустой комнате
        """
        return {
            "type": "empty"
        }


class BossRoom(BattleRoom):
    """Боссовая комната."""

    def __init__(self, position: int, total_rooms: int, enemies: List[Dict[str, Any]]):
        """
        Инициализирует боссовую комнату.
        
        Args:
            position: Позиция комнаты в последовательности
            total_rooms: Общее количество комнат
            enemies: Список врагов (обычно один сильный босс)
        """
        super().__init__(position, total_rooms, enemies)
        self.room_type = RoomType.BOSS
        self.description = "Вы нашли логово босса! Готовьтесь к серьезному бою!"