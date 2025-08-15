# game/ui/rendering/renderable.py
"""
Базовые элементы пользовательского интерфейса.

Содержит абстрактные и конкретные классы для отображаемых элементов
интерфейса: текст, кнопки, разделители и т.д.
"""

from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional
from game.ui.rendering.color_manager import Color
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.ui.rendering.renderer import Renderer

class Renderable(ABC):
    """Абстрактный базовый класс для всех отображаемых элементов."""

    def __init__(self, x: int = 0, y: int = 0):
        """
        Инициализация отображаемого элемента.
        
        Args:
            x: Координата X
            y: Координата Y
        """
        self.x = x
        self.y = y

    @abstractmethod
    def render(self, renderer: 'Renderer') -> None:
        """
        Отрисовка элемента.
        
        Args:
            renderer: Рендерер для отрисовки
        """
        pass


class Text(Renderable):
    """Текстовый элемент."""

    def __init__(self, text: str, x: int = 0, y: int = 0, 
                 bold: bool = False, dim: bool = False, color: Color = Color.DEFAULT):
        """
        Инициализация текстового элемента.
        
        Args:
            text: Отображаемый текст
            x: Координата X
            y: Координата Y
            bold: Жирный шрифт
            dim: Тусклый шрифт
            color: Цвет текста
        """
        super().__init__(x, y)
        self.text = text
        self.bold = bold
        self.dim = dim
        self.color = color

    def render(self, renderer: 'Renderer') -> None:
        """Отрисовка текста."""
        renderer.draw_text(self.text, self.x, self.y, self.bold, self.dim, self.color)


class TemplateText(Renderable):
    """Текст с шаблонами и цветами."""

    def __init__(self, template: str, replacements: Dict[str, Tuple[str, Color, bool, bool]], 
                 x: int = 0, y: int = 0):
        """
        Инициализация шаблонного текста.
        
        Args:
            template: Шаблон текста с плейсхолдерами %1, %2 и т.д.
            replacements: Словарь замен {номер: (текст, цвет, жирный, тусклый)}
            x: Координата X
            y: Координата Y
        """
        super().__init__(x, y)
        self.template = template
        self.replacements = replacements

    def render(self, renderer: 'Renderer') -> None:
        """Отрисовка шаблонного текста."""
        renderer.draw_template(self.template, self.replacements, self.x, self.y)


class Button(Renderable):
    """Кнопка."""

    def __init__(self, text: str, x: int = 0, y: int = 0, 
                 key: str = "", color: Color = Color.DEFAULT, bold: bool = False, dim: bool = False):
        """
        Инициализация кнопки.
        
        Args:
            text: Текст кнопки
            x: Координата X
            y: Координата Y
            key: Клавиша для активации
            color: Цвет текста
            bold: Жирный шрифт
            dim: Тусклый шрифт
        """
        super().__init__(x, y)
        self.text = text
        self.key = key
        self.color = color
        self.bold = bold
        self.dim = dim

    def render(self, renderer: 'Renderer') -> None:
        """Отрисовка кнопки."""
        display_text = f"[{self.key}] {self.text}" if self.key else self.text
        renderer.draw_text(display_text, self.x, self.y, self.bold, self.dim, self.color)


class Separator(Renderable):
    """Разделительная линия."""

    def __init__(self, y: int, char: str = "─", length: Optional[int] = None, 
                 color: Color = Color.RED, bold: bool = False, dim: bool = True):
        """
        Инициализация разделителя.
        
        Args:
            y: Координата Y
            char: Символ для линии
            length: Длина линии (None для автоматической)
            color: Цвет линии
            bold: Жирный шрифт
            dim: Тусклый шрифт
        """
        super().__init__(0, y)
        self.char = char
        self.length = length
        self.color = color
        self.bold = bold
        self.dim = dim

    def render(self, renderer: 'Renderer') -> None:
        """Отрисовка разделителя."""
        line_length = self.length or renderer.width
        line = self.char * (line_length - 1)
        renderer.draw_text(line, self.x, self.y, self.bold, self.dim, self.color)