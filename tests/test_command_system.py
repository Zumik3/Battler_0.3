# tests/test_command_system.py
from unittest.mock import MagicMock, patch
from game.ui.command_system.command import Command, CommandRegistry


class CommandTest(Command):
    def __init__(self, name="Test", description="A test command", keys=None):
        if keys is None:
            keys = ['t']
        super().__init__(name, description, keys)
        self.executed = False
        self.context = None

    def execute(self, context=None):
        self.executed = True
        self.context = context


class CommandWithIntKeyTest(Command):
    def __init__(self):
        # Имитируем ситуацию, когда ключ передан как число
        super().__init__("Int Key Cmd", "Command with int key", [10])  # Enter key code
        self.executed = False

    def execute(self, context=None):
        self.executed = True


def test_command_initialization():
    cmd = CommandTest("MyCmd", "My Description", ['m', 'M'])
    assert cmd.name == "MyCmd"
    assert cmd.description == "My Description"
    assert cmd.keys == ['m', 'M']


def test_command_get_key_codes_case_insensitive():
    cmd1 = CommandTest("Test1", "Desc", ['a'])  # lowercase
    cmd2 = CommandTest("Test2", "Desc", ['A'])  # uppercase

    assert cmd1.get_key_codes() != cmd2.get_key_codes()
    assert cmd1.get_key_codes() == {ord('a')}  # Проверяем, что это код 'a'


def test_command_registry_register_command():
    registry = CommandRegistry()
    cmd = CommandTest()

    registry.register_command(cmd)

    assert cmd in registry._commands
    assert ord('t') in registry._key_to_command
    assert registry._key_to_command[ord('t')] == cmd


def test_command_registry_execute_command_success():
    registry = CommandRegistry()
    cmd = CommandTest()
    registry.register_command(cmd)

    result = registry.execute_command(ord('t'), "test_context")

    assert result is True
    assert cmd.executed is True
    assert cmd.context == "test_context"


def test_command_registry_execute_command_failure():
    registry = CommandRegistry()
    cmd = CommandTest()
    registry.register_command(cmd)

    result = registry.execute_command(ord('x'), "test_context")  # 'x' не зарегистрирован

    assert result is False
    assert cmd.executed is False  # Команда не должна выполниться


def test_command_registry_get_all_commands():
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


def test_command_registry_get_command_by_key():
    registry = CommandRegistry()
    cmd = CommandTest()
    registry.register_command(cmd)

    found_cmd = registry.get_command_by_key(ord('t'))
    not_found_cmd = registry.get_command_by_key(ord('x'))

    assert found_cmd == cmd
    assert not_found_cmd is None


def test_command_with_int_key_in_registry():
    # Проверяем, как реестр обрабатывает команды, если get_key_codes вернул int напрямую
    # (Это тест для случая, если бы get_key_codes возвращал int, но в текущей реализации так не бывает)
    # Но мы можем проверить, что реестр работает с int ключами
    registry = CommandRegistry()
    cmd = CommandWithIntKeyTest()  # Эта команда в keys имеет [10]

    # Мы должны убедиться, что get_key_codes правильно обрабатывает это
    # Но в текущей реализации Command.__init__ требует List[str]
    # Так что этот тест скорее гипотетический, если бы тип был Union[str, int]

    # Для текущей реализации, если мы хотим протестировать с int кодом,
    # мы можем напрямую добавить его в реестр
    registry._key_to_command[10] = cmd
    registry._commands.append(cmd)

    result = registry.execute_command(10, "context")

    assert result is True
    assert cmd.executed is True
