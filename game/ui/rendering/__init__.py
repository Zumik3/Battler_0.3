# Game/UI/Rendering/__init__.py
"""
Модуль рендеринга пользовательского интерфейса.

Содержит компоненты для отрисовки текста, шаблонов, кнопок и других элементов
интерфейса с поддержкой цветов, форматирования и шаблонов.
"""

from .renderer import Renderer
from .renderable import Renderable, Text, TemplateText, Button, Separator
from .color_manager import Color, ColorManager
from .template_renderer import TemplatePart, TemplateRenderer

__all__ = [
    'Renderer',
    'Renderable', 'Text', 'TemplateText', 'Button', 'Separator',
    'Color', 'ColorManager',
    'TemplatePart', 'TemplateRenderer'
]