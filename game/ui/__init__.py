# game/ui/__init__.py
"""
Пакет пользовательского интерфейса игры.

Содержит все компоненты для отображения и взаимодействия с пользователем.
"""

# Импортируем основные компоненты для удобства
from .screen_manager import ScreenManager
from .base_screen import BaseScreen

__all__ = [
    'ScreenManager',
    'BaseScreen'
]