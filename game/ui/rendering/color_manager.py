# game/ui/rendering/color_manager.py
"""Управление цветами для пользовательского интерфейса.

Предоставляет систему цветов и управление цветовыми парами для curses.
"""

import curses
from enum import Enum
from typing import Any  # Для аннотации stdscr


class Color(Enum):
    """Перечисление доступных цветов."""
    DEFAULT = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7
    # Примечание: GRAY (8) может не поддерживаться всеми терминалами
    GRAY = 8


class ColorManager:
    """Управление цветами для curses."""

    def __init__(self) -> None:
        """Инициализация менеджера цветов."""
        self.color_pairs: dict = {}
        self._initialized = False

    def initialize(self, stdscr: Any) -> None:
        """
        Инициализация цветов.

        Args:
            stdscr: Окно curses для инициализации цветов.
        """
        if not self._initialized and curses.has_colors():
            curses.start_color()
            curses.use_default_colors()

            # Определяем цветовые пары
            curses.init_pair(Color.RED.value, curses.COLOR_RED, -1)
            curses.init_pair(Color.GREEN.value, curses.COLOR_GREEN, -1)
            curses.init_pair(Color.YELLOW.value, curses.COLOR_YELLOW, -1)
            curses.init_pair(Color.BLUE.value, curses.COLOR_BLUE, -1)
            curses.init_pair(Color.MAGENTA.value, curses.COLOR_MAGENTA, -1)
            curses.init_pair(Color.CYAN.value, curses.COLOR_CYAN, -1)
            curses.init_pair(Color.WHITE.value, curses.COLOR_WHITE, -1)
            # TODO: Проверить поддержку цвета 8 (GRAY) в различных терминалах
            curses.init_pair(Color.GRAY.value, 8, -1)

            self._initialized = True

    def get_color_pair(self, color: Color) -> int:
        """
        Получение цветовой пары.

        Args:
            color: Цвет из перечисления Color.

        Returns:
            Цветовая пара для curses.
        """
        if not self._initialized:
            return curses.A_NORMAL
        return curses.color_pair(color.value)
