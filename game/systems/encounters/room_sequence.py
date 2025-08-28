# game/systems/encounters/room_sequence.py
"""Управление последовательностью комнат в encounter'ах."""

from typing import List, Optional, Dict, Any
from game.systems.encounters.room import Room, RoomStatus


class RoomSequenceProgress:
    """Отслеживание прогресса последовательности комнат."""

    def __init__(self, total_rooms: int):
        """
        Инициализирует отслеживание прогресса.
        
        Args:
            total_rooms: Общее количество комнат
        """
        self.total_rooms = total_rooms
        self.completed_rooms = 0
        self.current_room_index = -1  # -1 означает, что последовательность еще не начата

    def start_sequence(self) -> None:
        """Начинает последовательность комнат."""
        self.current_room_index = 0

    def complete_current_room(self) -> None:
        """Помечает текущую комнату как пройденную."""
        if 0 <= self.current_room_index < self.total_rooms:
            self.completed_rooms += 1

    def advance_to_next_room(self) -> bool:
        """
        Переходит к следующей комнате.
        
        Returns:
            True, если переход успешен, False если это была последняя комната
        """
        if self.current_room_index < self.total_rooms - 1:
            self.current_room_index += 1
            return True
        return False

    def is_completed(self) -> bool:
        """
        Проверяет, завершена ли вся последовательность.
        
        Returns:
            True, если все комнаты пройдены
        """
        return self.completed_rooms >= self.total_rooms

    def get_progress_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о прогрессе.
        
        Returns:
            Словарь с информацией о прогрессе
        """
        return {
            "total_rooms": self.total_rooms,
            "completed_rooms": self.completed_rooms,
            "current_room_index": self.current_room_index,
            "progress_percentage": (self.completed_rooms / self.total_rooms) * 100 if self.total_rooms > 0 else 0,
            "is_completed": self.is_completed()
        }


class RoomSequence:
    """Последовательность комнат в encounter'е."""

    def __init__(self, rooms: List[Room]):
        """
        Инициализирует последовательность комнат.
        
        Args:
            rooms: Список комнат в порядке их следования
        """
        self.rooms = rooms
        self.progress = RoomSequenceProgress(len(rooms))
        self.name = f"Последовательность комнат ({len(rooms)} комнат)"
        self.description = "Последовательность комнат для прохождения"

    def start(self) -> Optional[Room]:
        """
        Начинает последовательность и возвращает первую комнату.
        
        Returns:
            Первая комната или None, если последовательность пуста
        """
        if not self.rooms:
            return None
            
        self.progress.start_sequence()
        first_room = self.rooms[0]
        first_room.activate()
        return first_room

    def get_current_room(self) -> Optional[Room]:
        """
        Возвращает текущую активную комнату.
        
        Returns:
            Текущая комната или None, если последовательность не начата
        """
        if 0 <= self.progress.current_room_index < len(self.rooms):
            return self.rooms[self.progress.current_room_index]
        return None

    def complete_current_room(self) -> None:
        """Помечает текущую комнату как пройденную."""
        current_room = self.get_current_room()
        if current_room:
            current_room.complete()
            self.progress.complete_current_room()

    def advance_to_next_room(self) -> Optional[Room]:
        """
        Переходит к следующей комнате.
        
        Returns:
            Следующая комната или None, если это была последняя комната
        """
        if self.progress.advance_to_next_room():
            next_room = self.get_current_room()
            if next_room:
                next_room.activate()
            return next_room
        return None

    def is_completed(self) -> bool:
        """
        Проверяет, завершена ли вся последовательность.
        
        Returns:
            True, если все комнаты пройдены
        """
        return self.progress.is_completed()

    def get_progress_info(self) -> Dict[str, Any]:
        """
        Возвращает информацию о прогрессе последовательности.
        
        Returns:
            Словарь с информацией о прогрессе
        """
        base_info = self.progress.get_progress_info()
        current_room_info = {}
        
        current_room = self.get_current_room()
        if current_room:
            current_room_info = current_room.get_progress_info()
            
        return {
            **base_info,
            "current_room": current_room_info,
            "sequence_name": self.name,
            "sequence_description": self.description
        }

    def get_total_rooms(self) -> int:
        """
        Возвращает общее количество комнат.
        
        Returns:
            Количество комнат
        """
        return len(self.rooms)

    def get_completed_rooms_count(self) -> int:
        """
        Возвращает количество пройденных комнат.
        
        Returns:
            Количество пройденных комнат
        """
        return self.progress.completed_rooms

    def get_remaining_rooms_count(self) -> int:
        """
        Возвращает количество оставшихся комнат.
        
        Returns:
            Количество оставшихся комнат
        """
        return self.get_total_rooms() - self.get_completed_rooms_count()

    def set_name(self, name: str) -> None:
        """
        Устанавливает имя последовательности.
        
        Args:
            name: Имя последовательности
        """
        self.name = name

    def set_description(self, description: str) -> None:
        """
        Устанавливает описание последовательности.
        
        Args:
            description: Описание последовательности
        """
        self.description = description