# game/ui/command_system/command.py
"""Базовые классы для системы команд.

Реализует паттерн Команда для обработки пользовательского ввода.
"""

from abc import ABC, abstractmethod
import curses
from typing import List, Set, Optional, Any, Union, Callable

# Отложенная аннотация для избежения циклического импорта
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.ui.base_screen import BaseScreen


class Command(ABC):
    """Абстрактная команда."""

    def __init__(self, name: str, description: str, keys: List[Union[str, int]], display_key: str = ""):
        """
        Инициализация команды.

        Args:
            name: Название команды.
            description: Описание команды.
            keys: Список клавиш, на которые назначена команда (например, ['q', 'ESC']).
            display_key: Клавиша для отображения в интерфейсе (если отличается от первой в keys).
        """
        self.name = name
        self.description = description
        self.keys = keys  # Список символов, например ['q', 'ESC']
        self.display_key = display_key if display_key else (str(keys[0]) if keys else "")

    def get_key_codes(self) -> Set[int]:
        """Получение множества кодов клавиш команды."""
        # ord работает только со строками, числа возвращаем как есть
        return {key if isinstance(key, int) else ord(key) for key in self.keys}

    @abstractmethod
    def execute(self, context: Any = None) -> None:
        """
        Выполнение команды.
        
        Args:
            context: Контекст выполнения команды.
            
        Returns:
            bool: True если команда выполнена успешно, False в противном случае.
        """
        raise NotImplementedError("Метод execute должен быть реализован в подклассе.")

class LambdaCommand(Command):
    """Команда, выполняющая переданную функцию."""
    def __init__(self, name: str, description: str, keys: List[Union[str, int]], action: Callable[[Any], None], display_key: str = ""):
        super().__init__(name, description, keys, display_key)
        self.action = action

    def execute(self, context: Any = None) -> None:
        self.action(context)


class CommandRegistry:
    """Реестр команд для экрана."""

    def __init__(self) -> None:
        self._commands: List[Command] = []
        self._key_to_command: dict[int, Command] = {}  # key_code -> command

    def register_command(self, command: Command) -> None:
        """
        Регистрация команды.

        Args:
            command: Команда для регистрации.
        """
        self._commands.append(command)
        # Регистрируем все клавиши команды
        for key_code in command.get_key_codes():
            self._key_to_command[key_code] = command

    def execute_command(self, key_code: int, context: Optional[Any] = None) -> bool:
        """
        Выполнение команды по коду клавиши.

        Args:
            key_code: Код нажатой клавиши.
            context: Контекст выполнения.

        Returns:
            True если команда найдена и выполнена, False если нет.
        """
        command = self._key_to_command.get(key_code)
        if command:
            command.execute(context)
            return True
        return False

    def get_all_commands(self) -> List[Command]:
        """Получение всех зарегистрированных команд."""
        return self._commands.copy()

    def get_command_by_key(self, key_code: int) -> Optional[Command]:
        """Получение команды по коду клавиши."""
        return self._key_to_command.get(key_code)

    def clear(self) -> None:
        self._commands.clear()
