# tests/test_command_system.py
"""Тесты для системы команд."""

from typing import Any, Optional
from unittest.mock import MagicMock, patch

from game.ui.command_system.command import Command, CommandRegistry


class CommandTest(Command):
    """Тестовая реализация команды."""

    def __init__(self, name: str = "Test", description: str = "A test command", keys: Optional[list] = None) -> None:
        """
        Инициализация тестовой команды.

        Args:
            name: Название команды.
            description: Описание команды.
            keys: Список клавиш.
        """
        if keys is None:
            keys = ['t']
        super().__init__(name, description, keys)
        self.executed: bool = False
        self.context: Any = None

    def execute(self, context: Any = None) -> None:
        """
        Выполнение тестовой команды.

        Args:
            context: Контекст выполнения.
        """
        self.executed = True
        self.context = context


class CommandWithIntKeyTest(Command):
    """Тестовая реализация команды с целочисленным кодом клавиши."""

    def __init__(self) -> None:
        """Инициализация команды с целочисленным кодом клавиши."""
        # Имитируем ситуацию, когда ключ передан как число
        super().__init__("Int Key Cmd", "Command with int key", [10])  # Enter key code
        self.executed: bool = False

    def execute(self, context: Any = None) -> None:
        """
        Выполнение команды с целочисленным кодом клавиши.

        Args:
            context: Контекст выполнения.
        """
        self.executed = True


def test_command_initialization() -> None:
    """Тест инициализации команды."""
    cmd = CommandTest("MyCmd", "My Description", ['m', 'M'])
    assert cmd.name == "MyCmd"
    assert cmd.description == "My Description"
    assert cmd.keys == ['m', 'M']


def test_command_get_key_codes_case_insensitive() -> None:
    """Тест получения кодов клавиш с учетом регистра."""
    cmd1 = CommandTest("Test1", "Desc", ['a'])  # lowercase
    cmd2 = CommandTest("Test2", "Desc", ['A'])  # uppercase

    assert cmd1.get_key_codes() != cmd2.get_key_codes()
    assert cmd1.get_key_codes() == {ord('a')}  # Проверяем, что это код 'a'


def test_command_registry_register_command() -> None:
    """Тест регистрации команды в реестре."""
    registry = CommandRegistry()
    cmd = CommandTest()

    registry.register_command(cmd)

    assert cmd in registry._commands
    assert ord('t') in registry._key_to_command
    assert registry._key_to_command[ord('t')] == cmd


def test_command_registry_execute_command_success() -> None:
    """Тест успешного выполнения команды из реестра."""
    registry = CommandRegistry()
    cmd = CommandTest()
    registry.register_command(cmd)

    result = registry.execute_command(ord('t'), "test_context")

    assert result is True
    assert cmd.executed is True
    assert cmd.context == "test_context"


def test_command_registry_execute_command_failure() -> None:
    """Тест неуспешного выполнения команды из реестра."""
    registry = CommandRegistry()
    cmd = CommandTest()
    registry.register_command(cmd)

    result = registry.execute_command(ord('x'), "test_context")  # 'x' не зарегистрирован

    assert result is False
    assert cmd.executed is False  # Команда не должна выполниться


def test_command_registry_get_all_commands() -> None:
    """Тест получения всех команд из реестра."""
    registry = CommandRegistry()
    cmd1 = CommandTest("Cmd1", "Desc1", ['1'])
    cmd2 = CommandTest("Cmd2", "Desc2", ['2'])

    registry.register_command(cmd1)
    registry.register_command(cmd2)

    all_commands = registry.get_all_commands()

    assert len(all_commands) == 2
    assert cmd1 in all_commands
    assert cmd2 in all_commands
    # Проверяем, что возвращается копия
    assert all_commands is not registry._commands


def test_command_registry_get_command_by_key() -> None:
    """Тест получения команды по коду клавиши из реестра."""
    registry = CommandRegistry()
    cmd = CommandTest()
    registry.register_command(cmd)

    found_cmd = registry.get_command_by_key(ord('t'))
    not_found_cmd = registry.get_command_by_key(ord('x'))

    assert found_cmd == cmd
    assert not_found_cmd is None


def test_command_with_int_key_in_registry() -> None:
    """Тест работы реестра с командой, имеющей целочисленный код клавиши."""
    # Проверяем, как реестр обрабатывает команды с int ключами
    registry = CommandRegistry()
    cmd = CommandWithIntKeyTest()  # Эта команда в keys имеет [10]

    # Регистрируем команду через реестр, который должен корректно обработать int ключ
    registry.register_command(cmd)

    # Выполняем команду по её int коду
    result = registry.execute_command(10, "context")

    assert result is True
    assert cmd.executed is True
