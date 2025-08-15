# game/ui/commands/inventory_commands.py
"""
Специфические команды для экрана инвентаря.
"""

from curses import KEY_ENTER
from game.ui.command_system.command import Command
from game.ui.inventory_screen import InventoryScreen
from game.ui.command_system.screen_command_registry import register_screen_commands
from typing import Optional, Any


class UseItemCommand(Command):
    """Команда использования предмета."""

    def __init__(self):
        super().__init__(
            name="Использовать",
            description="Использовать выбранный предмет",
            keys=['u', KEY_ENTER],
            display_key="u/Enter"
        )

    def execute(self, context: Optional[Any] = None) -> None:
        """Выполнение команды использования предмета."""
        if context:
            print("Предмет использован")


class DropItemCommand(Command):
    """Команда выбрасывания предмета."""

    def __init__(self):
        super().__init__(
            name="Выбросить",
            description="Выбросить выбранный предмет",
            keys=['d'],
            display_key="d"
        )

    def execute(self, context: Optional[Any] = None) -> None:
        """Выполнение команды выбрасывания предмета."""
        if context:
            print("Предмет выброшен")


# Импортируем общие команды
from game.ui.commands.common_commands import GoBackCommand

# Регистрируем команды для экрана инвентаря
register_screen_commands(InventoryScreen, [
    UseItemCommand(),
    DropItemCommand(),
    GoBackCommand()  # Переиспользуем общую команду
])