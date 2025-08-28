# game/ui/commands/main_screen_commands.py
"""Специфические команды для главного экрана."""

from typing import Optional, Any

from game.ui.command_system.command import Command
from game.ui.command_system.screen_command_registry import register_screen_commands
# Импортируем общие команды
from game.ui.commands.common_commands import OpenInventoryCommand, ExitCommand
# Импортируем экран для регистрации команд
from game.ui.main_screen import MainScreen


class StartEncounterCommand(Command):
    """Команда для перехода к выбору похода."""

    def __init__(self):
        super().__init__(
            name="Поход",
            description="Начать поход",
            keys=['1'],
            display_key="1"
        )

    def execute(self, context: Optional[Any] = None) -> None:
        """Выполнение команды."""
        if context and hasattr(context, 'manager'):
            context.manager.change_screen("encounter_selection")


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
        # TODO: Заменить print на отображение внутри curses UI
        if context:
            print("Открытие настроек")


# Регистрируем команды для главного экрана
register_screen_commands(MainScreen, [
    StartEncounterCommand(),
    OpenInventoryCommand(),
    OpenSettingsCommand(),
    ExitCommand()
])
