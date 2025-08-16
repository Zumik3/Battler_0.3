# game/ui/command_system/command_renderer.py
"""Отрисовка команд пользовательского интерфейса.

Отдельный класс для отображения информации о доступных командах.
"""

from typing import List, TYPE_CHECKING

from game.ui.rendering.color_manager import Color
from game.ui.rendering.renderable import Text

if TYPE_CHECKING:
    from game.ui.command_system.command import Command


class CommandRenderer:
    """Обработчик отображения списка доступных команд."""

    def __init__(self, x: int = 0, y: int = 15, max_width: int = 70):
        """
        Инициализация отрисовщика команд.

        Args:
            x: Начальная координата X.
            y: Начальная координата Y.
            max_width: Максимальная ширина строки команд.
        """
        self.x = x
        self.y = y
        self.max_width = max_width

    def render_commands(self, commands: List['Command']) -> List[Text]:
        """
        Создание элементов отрисовки для команд в одной строке.
        Команды отображаются в формате "key : описание", разделенные " | ".
        Все элементы - тускло серые.

        Args:
            commands: Список команд для отрисовки.

        Returns:
            Список текстовых элементов для отрисовки.
        """
        if not commands:
            return []

        # Создаем список строк для каждой команды и объединяем их
        command_strings = [f"{command.display_key} : {command.name}" for command in commands]
        full_line = " | ".join(command_strings)

        # Возвращаем один текстовый элемент, весь текст будет тускло серым
        return [Text(full_line, self.x, self.y, dim=True, color=Color.GRAY)]
