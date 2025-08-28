# game/ui/components/room_sequence_components.py
"""UI компоненты для отображения прогресса последовательности комнат."""

from typing import Dict, Any
from game.ui.rendering.renderable import Renderable
from game.ui.rendering.renderer import Renderer


class RoomProgressIndicator(Renderable):
    """Индикатор прогресса по комнатам."""

    def __init__(self, x: int, y: int, total_rooms: int, completed_rooms: int):
        """
        Инициализирует индикатор прогресса.
        
        Args:
            x: Координата X
            y: Координата Y
            total_rooms: Общее количество комнат
            completed_rooms: Количество пройденных комнат
        """
        self.x = x
        self.y = y
        self.total_rooms = total_rooms
        self.completed_rooms = completed_rooms

    def render(self, renderer: Renderer) -> None:
        """Отрисовывает индикатор прогресса."""
        # Создаем визуальное представление прогресса
        progress_text = f"Прогресс: {self.completed_rooms}/{self.total_rooms} комнат"
        renderer.draw_text(progress_text, self.x, self.y)

        # Создаем визуальную полосу прогресса
        if self.total_rooms > 0:
            progress_ratio = self.completed_rooms / self.total_rooms
            bar_width = 20
            filled_width = int(bar_width * progress_ratio)
            
            # Рисуем пустую полосу
            renderer.draw_text("[" + " " * bar_width + "]", self.x, self.y + 1)
            
            # Рисуем заполненную часть
            if filled_width > 0:
                filled_bar = "[" + "=" * filled_width
                renderer.draw_text(filled_bar, self.x, self.y + 1)


class SequenceStatusPanel(Renderable):
    """Панель статуса последовательности комнат."""

    def __init__(self, x: int, y: int, sequence_info: Dict[str, Any]):
        """
        Инициализирует панель статуса.
        
        Args:
            x: Координата X
            y: Координата Y
            sequence_info: Информация о последовательности
        """
        self.x = x
        self.y = y
        self.sequence_info = sequence_info

    def render(self, renderer: Renderer) -> None:
        """Отрисовывает панель статуса."""
        # Отображаем информацию о последовательности
        name = self.sequence_info.get("sequence_name", "Последовательность комнат")
        renderer.draw_text(name, self.x, self.y, bold=True)
        
        # Отображаем текущую комнату
        current_room_info = self.sequence_info.get("current_room", {})
        if current_room_info:
            position = current_room_info.get("position", 0) + 1  # 1-indexed для отображения
            total = current_room_info.get("total_rooms", 0)
            room_status = current_room_info.get("status", "unknown")
            
            status_text = f"Комната {position}/{total} (Статус: {room_status})"
            renderer.draw_text(status_text, self.x, self.y + 1)
            
            # Отображаем описание комнаты
            room_description = current_room_info.get("description", "")
            if room_description:
                renderer.draw_text(room_description, self.x, self.y + 2, dim=True)


class RoomMap(Renderable):
    """Карта комнат (простая визуализация)."""

    def __init__(self, x: int, y: int, total_rooms: int, current_room_index: int):
        """
        Инициализирует карту комнат.
        
        Args:
            x: Координата X
            y: Координата Y
            total_rooms: Общее количество комнат
            current_room_index: Индекс текущей комнаты
        """
        self.x = x
        self.y = y
        self.total_rooms = total_rooms
        self.current_room_index = current_room_index

    def render(self, renderer: Renderer) -> None:
        """Отрисовывает карту комнат."""
        # Простая линейная визуализация комнат
        map_line = ""
        for i in range(self.total_rooms):
            if i == self.current_room_index:
                map_line += "[*]"  # Текущая комната
            elif i < self.current_room_index:
                map_line += "[x]"  # Пройденная комната
            else:
                map_line += "[ ]"  # Непройденная комната
            
            if i < self.total_rooms - 1:
                map_line += "-"
        
        renderer.draw_text("Карта: " + map_line, self.x, self.y)