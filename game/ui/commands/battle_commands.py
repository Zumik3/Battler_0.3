# game/ui/commands/battle_commands.py
"""
Специфические команды для экрана боя.
"""

from game.ui.command_system.command import Command
from game.ui.battle_screen import BattleScreen
from game.ui.command_system.screen_command_registry import register_screen_commands
from typing import Optional, Any


class AttackCommand(Command):
    """Команда атаки."""

    def __init__(self):
        super().__init__(
            name="Атака",
            description="Атаковать противника",
            keys=['a', 'A'],
            display_key="A/a"
        )

    def execute(self, context: Optional[Any] = None) -> None:
        """Выполнение команды атаки."""
        if context:
            print("Атака!")


class DefendCommand(Command):
    """Команда защиты."""

    def __init__(self):
        super().__init__(
            name="Защита",
            description="Защититься от атаки",
            keys=['d'],
            display_key="d"
        )

    def execute(self, context: Optional[Any] = None) -> None:
        """Выполнение команды защиты."""
        if context:
            print("Защита!")


class MagicCommand(Command):
    """Команда использования магии."""

    def __init__(self):
        super().__init__(
            name="Магия",
            description="Использовать магическое заклинание",
            keys=['m'],
            display_key="m"
        )

    def execute(self, context: Optional[Any] = None) -> None:
        """Выполнение команды магии."""
        if context:
            print("Магия!")


# Импортируем общие команды
from game.ui.commands.common_commands import GoBackCommand, OpenInventoryCommand

# Регистрируем команды для экрана боя
register_screen_commands(BattleScreen, [
    AttackCommand(),
    DefendCommand(),
    MagicCommand(),
    OpenInventoryCommand(),  # Переиспользуем общую команду
    GoBackCommand()          # Переиспользуем общую команду
])