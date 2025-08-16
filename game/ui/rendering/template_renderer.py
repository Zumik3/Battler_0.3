# game/ui/rendering/template_renderer.py
"""Рендерер для работы с шаблонами текста.

Позволяет создавать форматированный текст с плейсхолдерами и различными
стилями для каждой части текста.
"""

import re
from typing import Dict, List, Tuple, Any

import curses

from game.ui.rendering.color_manager import Color, ColorManager


class TemplatePart:
    """Часть шаблона с форматированием."""

    def __init__(self, text: str, color: Color = Color.DEFAULT, bold: bool = False, dim: bool = False):
        """
        Инициализация части шаблона.

        Args:
            text: Текст части.
            color: Цвет текста.
            bold: Жирный шрифт.
            dim: Тусклый шрифт.
        """
        self.text = text
        self.color = color
        self.bold = bold
        self.dim = dim


class TemplateRenderer:
    """Рендерер для работы с шаблонами текста."""

    def __init__(self, color_manager: ColorManager) -> None:
        """
        Инициализация рендерера шаблонов.

        Args:
            color_manager: Менеджер цветов для применения стилей.
        """
        self.color_manager = color_manager
        # Регулярное выражение для поиска плейсхолдеров типа %1, %2 и т.д.
        self.placeholder_pattern = re.compile(r'%(\d+)')

    def render_template(self, template: str,
                       replacements: Dict[str, Tuple[str, Color, bool, bool]]) -> List[TemplatePart]:
        """
        Рендер шаблона с заменами.

        Args:
            template: Шаблон текста, например "%1 ударяет %2".
            replacements: Словарь {номер: (текст, цвет, жирный, тусклый)}, например {"1": ("Игрок", Color.GREEN, True, False)}.

        Returns:
            Список частей текста с форматированием.
        """
        parts: List[TemplatePart] = []
        last_end = 0

        # Находим все плейсхолдеры
        for match in self.placeholder_pattern.finditer(template):
            start, end = match.span()
            placeholder_num = match.group(1)

            # Добавляем текст до плейсхолдера
            if start > last_end:
                parts.append(TemplatePart(template[last_end:start]))

            # Добавляем замену для плейсхолдера
            if placeholder_num in replacements:
                text, color, bold, dim = replacements[placeholder_num]
                parts.append(TemplatePart(text, color, bold, dim))
            else:
                # Если нет замены, оставляем плейсхолдер как есть
                parts.append(TemplatePart(match.group(0)))

            last_end = end

        # Добавляем оставшийся текст
        if last_end < len(template):
            parts.append(TemplatePart(template[last_end:]))

        return parts

    def draw_template(self, stdscr: curses.window, template: str, replacements: Dict[str, Tuple[str, Color, bool, bool]],
                     x: int, y: int) -> None:
        """
        Отрисовка шаблона на экране.

        Args:
            stdscr: Окно curses для отрисовки.
            template: Шаблон текста.
            replacements: Словарь замен.
            x: Координата X.
            y: Координата Y.
        """
        try:
            parts = self.render_template(template, replacements)
            current_x = x

            for part in parts:
                if y >= 0 and current_x >= 0:
                    attr = self.color_manager.get_color_pair(part.color)
                    if part.bold:
                        attr |= curses.A_BOLD
                    if part.dim:
                        attr |= curses.A_DIM

                    stdscr.addstr(y, current_x, part.text, attr)
                    current_x += len(part.text)
        except curses.error:
            # Игнорируем ошибки выхода за границы экрана
            pass
