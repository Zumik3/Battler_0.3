# game/ui/base_screen.py
import curses
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List
from game.ui.rendering.renderable import Renderable
from game.ui.rendering.renderer import Renderer
from game.ui.command_system import CommandRegistry
from game.ui.command_system.screen_command_registry import get_screen_commands

if TYPE_CHECKING:
    from game.ui.screen_manager import ScreenManager
    from game.ui.command_system.command import Command # Импортируем Command для аннотаций

class BaseScreen(ABC):
    """Абстрактный базовый класс для всех экранов."""
    def __init__(self, manager: 'ScreenManager'):
        self.manager = manager
        self.elements: List[Renderable] = []
        self.renderer: Renderer = manager.renderer
        self.command_registry = CommandRegistry()
        self._setup_elements()
        self._setup_commands()
        self._setup_auto_commands()

    @abstractmethod
    def _setup_elements(self) -> None:
        """Настройка элементов экрана."""
        pass

    @abstractmethod
    def _setup_commands(self) -> None:
        """Настройка дополнительных команд экрана."""
        pass

    def _setup_auto_commands(self) -> None:
        """Автоматическая регистрация команд из реестра."""
        # Явно аннотируем тип возвращаемого значения get_screen_commands
        commands: List['Command'] = get_screen_commands(self.__class__)
        # Явно аннотируем тип переменной command в цикле
        command: 'Command'
        for command in commands:
            self.add_command(command) # <-- Эта строка вызывала ошибку mypy

    def add_command(self, command: 'Command') -> None: # <-- Убедитесь, что тип команды аннотирован здесь
        """
        Добавление команды на экран.
        Args:
            command: Команда для добавления
        """
        self.command_registry.register_command(command)

    def render(self, stdscr: curses.window) -> None:
        """Отрисовка экрана."""
        self.renderer.clear()
        # Отрисовка основных элементов
        for element in self.elements:
            element.render(self.renderer)
        # Базовый класс НЕ отрисовывает команды.
        # Это responsibility конкретных экранов или миксинов.
        # Отрисовка команд убрана отсюда.

    def handle_input(self, key: int) -> None:
        """
        Обработка ввода пользователя.
        Args:
            key: Нажатая клавиша
        """
        # Пытаемся выполнить команду, если не удалось - вызываем обработчик по умолчанию
        if not self.command_registry.execute_command(key, self):
            self._handle_unregistered_key(key)

    def _handle_unregistered_key(self, key: int) -> None:
        """
        Обработка назарегистрированных клавиш.
        Может быть переопределен в подклассах.
        """
        pass