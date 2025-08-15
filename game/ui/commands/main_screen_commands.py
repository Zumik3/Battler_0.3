# game/ui/commands/main_screen_commands.py
"""
Специфические команды для главного экрана.
"""

from game.ui.command_system.command import Command
from game.ui.main_screen import MainScreen
from game.ui.command_system.screen_command_registry import register_screen_commands
from typing import Optional, Any


class StartBattleCommand(Command):
    """Команда начала боя."""

    def __init__(self):
        super().__init__(
            name="Бой",
            description="Начать бой",
            keys=[10],
            display_key="Enter"
        )

    def execute(self, context: Optional[Any] = None) -> None:
        """Выполнение команды начала боя."""
        if context and hasattr(context, 'manager'):
            context.manager.change_screen("battle")


class OpenSettingsCommand(Command):
    """Команда открытия настроек."""

    def __init__(self):
        super().__init__(
            name="Настройки",
            description="Открыть настройки",
            keys=['3'],
            display_key="3"
        )

    def execute(self, context: Optional[Any] = None) -> None:
        """Выполнение команды открытия настроек."""
        if context:
            print("Открытие настроек")


# Импортируем общие команды
from game.ui.commands.common_commands import OpenInventoryCommand, ExitCommand

# Регистрируем команды для главного экрана
register_screen_commands(MainScreen, [
    StartBattleCommand(),
    OpenInventoryCommand(),  # Переиспользуем общую команду
    OpenSettingsCommand(),
    ExitCommand()            # Переиспользуем общую команду
])