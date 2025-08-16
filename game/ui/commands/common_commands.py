# game/ui/commands/common_commands.py
"""Общие команды, которые могут использоваться в нескольких экранах."""

from typing import Optional, Any

from game.ui.command_system.command import Command


class GoBackCommand(Command):
    """Общая команда возврата назад."""

    def __init__(self):
        super().__init__(
            name="Назад",
            description="Вернуться к предыдущему экрану",
            keys=['q'],
            display_key="q"
        )

    def execute(self, context: Optional[Any] = None) -> None:
        """Выполнение команды возврата."""
        if context and hasattr(context, 'manager'):
            context.manager.go_back()


class OpenInventoryCommand(Command):
    """Общая команда открытия инвентаря."""

    def __init__(self):
        super().__init__(
            name="Инвентарь",
            description="Открыть инвентарь",
            keys=['i'],
            display_key="i"
        )

    def execute(self, context: Optional[Any] = None) -> None:
        """Выполнение команды открытия инвентаря."""
        if context and hasattr(context, 'manager'):
            context.manager.change_screen("inventory")


class HelpCommand(Command):
    """Общая команда помощи."""

    def __init__(self):
        super().__init__(
            name="Помощь",
            description="Показать помощь",
            keys=['h', '?'],
            display_key="h/?"
        )

    def execute(self, context: Optional[Any] = None) -> None:
        """Выполнение команды помощи."""
        # TODO: Заменить print на отображение внутри curses UI
        if context:
            print("Помощь по экрану:", context.__class__.__name__ if context else "Неизвестный экран")


class ExitCommand(Command):
    """Общая команда выхода из игры."""

    def __init__(self):
        super().__init__(
            name="Выход",
            description="Выйти из игры",
            keys=['q'],  # Только q, не ESC чтобы избежать конфликтов
            display_key="q"
        )

    def execute(self, context: Optional[Any] = None) -> None:
        """Выполнение команды выхода."""
        # TODO: Рассмотреть использование raise SystemExit() вместо exit()
        exit()
