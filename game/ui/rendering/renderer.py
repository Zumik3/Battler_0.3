# Game/UI/Rendering/renderer.py
"""
Рендерер для отрисовки элементов пользовательского интерфейса.

Предоставляет абстракцию над библиотекой curses для упрощения отрисовки
текста, шаблонов и других элементов интерфейса.
"""

import curses
from typing import Dict, Tuple
from game.ui.rendering.color_manager import Color
from game.ui.rendering.template_renderer import TemplateRenderer


class Renderer:
    """Рендерер для отрисовки элементов на экране."""

    def __init__(self, stdscr: curses.window, color_manager):
        """
        Инициализация рендерера.
        
        Args:
            stdscr: Окно curses для отрисовки
            color_manager: Менеджер цветов
        """
        self.stdscr = stdscr
        self.color_manager = color_manager
        self.template_renderer = TemplateRenderer(color_manager)
        self.height, self.width = stdscr.getmaxyx()

    def clear(self) -> None:
        """Очистка экрана."""
        self.stdscr.clear()

    def draw_text(self, text: str, x: int, y: int, 
                  bold: bool = False, dim: bool = False, color: Color = Color.DEFAULT) -> None:
        """
        Отрисовка текста на экране.
        
        Args:
            text: Текст для отрисовки
            x: Координата X
            y: Координата Y
            bold: Жирный шрифт
            dim: Тусклый шрифт
            color: Цвет текста
        """
        try:
            # Проверяем границы экрана
            if y >= self.height or x >= self.width or y < 0 or x < 0:
                return
                
            # Получаем атрибуты
            attr = self.color_manager.get_color_pair(color)
            if bold:
                attr |= curses.A_BOLD
            if dim:
                attr |= curses.A_DIM
                
            self.stdscr.addstr(y, x, text, attr)
        except curses.error:
            # Игнорируем ошибки выхода за границы экрана
            pass

    def draw_template(self, template: str, replacements: Dict[str, Tuple[str, Color, bool, bool]], 
                      x: int, y: int) -> None:
        """
        Отрисовка шаблонного текста.
        
        Args:
            template: Шаблон текста с плейсхолдерами %1, %2 и т.д.
            replacements: Словарь замен {номер: (текст, цвет, жирный, тусклый)}
            x: Координата X
            y: Координата Y
        """
        try:
            # Проверяем границы экрана
            if y < 0 or x < 0 or y >= self.height:
                return
                
            self.template_renderer.draw_template(self.stdscr, template, replacements, x, y)
        except curses.error:
            pass

    def draw_box(self, x: int, y: int, width: int, height: int) -> None:
        """
        Отрисовка прямоугольника.
        
        Args:
            x: Координата X левого верхнего угла
            y: Координата Y левого верхнего угла
            width: Ширина прямоугольника
            height: Высота прямоугольника
        """
        try:
            # Верхняя и нижняя границы
            if y < self.height and y + height - 1 < self.height:
                self.stdscr.addstr(y, x, "+" + "-" * (width - 2) + "+")
                self.stdscr.addstr(y + height - 1, x, "+" + "-" * (width - 2) + "+")
            
            # Боковые границы
            for i in range(1, min(height - 1, self.height - y)):
                if y + i < self.height:
                    self.stdscr.addstr(y + i, x, "|")
                    if x + width - 1 < self.width:
                        self.stdscr.addstr(y + i, x + width - 1, "|")
        except curses.error:
            pass

    def refresh(self) -> None:
        """Обновление экрана."""
        self.stdscr.refresh()