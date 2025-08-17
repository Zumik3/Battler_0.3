# tests/test_ui/test_base_screen.py
"""Тесты для game/ui/base_screen.py"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import curses

# Импортируем тестируемый класс
# Поскольку BaseScreen абстрактный, мы создадим фиктивный подкласс для тестирования
from game.ui.base_screen import BaseScreen


class TestBaseScreen(unittest.TestCase):
    """Тесты для базового класса экрана."""

    def setUp(self) -> None:
        """Настройка тестового окружения перед каждым тестом."""
        # Мокаем зависимости
        self.mock_screen_manager = Mock()
        self.mock_renderer = Mock()
        # Явно мокаем методы clear и refresh у renderer
        self.mock_renderer.clear = Mock()
        self.mock_renderer.refresh = Mock()
        self.mock_screen_manager.renderer = self.mock_renderer

        # Мокаем функцию получения команд
        patcher_get_screen_commands = patch('game.ui.base_screen.get_screen_commands')
        self.mock_get_screen_commands = patcher_get_screen_commands.start()
        self.addCleanup(patcher_get_screen_commands.stop)

        # Мокаем класс CommandRegistry
        patcher_command_registry_class = patch('game.ui.base_screen.CommandRegistry')
        self.mock_command_registry_class = patcher_command_registry_class.start()
        self.addCleanup(patcher_command_registry_class.stop)

        # Создаем мок для экземпляра CommandRegistry
        self.mock_command_registry_instance = Mock()
        self.mock_command_registry_class.return_value = self.mock_command_registry_instance

        # Создаем фиктивный подкласс, чтобы обойти абстрактность BaseScreen
        # Это нужно только для вызова __init__
        class ConcreteBaseScreen(BaseScreen):
            def _setup_elements(self) -> None:
                pass # Реализация для обхода абстрактности
            
            def _setup_commands(self) -> None:
                pass # Реализация для обхода абстрактности

        self.ConcreteBaseScreen = ConcreteBaseScreen

    def test_init_initializes_attributes(self) -> None:
        """Тест инициализации атрибутов в __init__."""
        # Настройка моков
        mock_commands = [Mock(), Mock()]
        self.mock_get_screen_commands.return_value = mock_commands

        # Создание экземпляра
        screen = self.ConcreteBaseScreen(self.mock_screen_manager)

        # Проверки
        self.assertEqual(screen.manager, self.mock_screen_manager)
        self.assertEqual(screen.renderer, self.mock_renderer)
        self.mock_command_registry_class.assert_called_once()
        self.assertEqual(screen.command_registry, self.mock_command_registry_instance)
        # Проверяем, что get_screen_commands был вызван с правильным классом
        self.mock_get_screen_commands.assert_called_once_with(self.ConcreteBaseScreen)
        # Проверяем, что команды были зарегистрированы
        # Команды регистрируются через register_command
        expected_calls = [call(cmd) for cmd in mock_commands]
        self.mock_command_registry_instance.register_command.assert_has_calls(expected_calls, any_order=False)
        self.assertEqual(screen.elements, [])

    def test_handle_input_with_registered_command(self) -> None:
        """Тест handle_input при нажатии клавиши с зарегистрированной командой."""
        # Создание экземпляра
        screen = self.ConcreteBaseScreen(self.mock_screen_manager)

        # Настройка моков после создания экземпляра
        mock_command = Mock()
        # Мокаем execute_command так, чтобы он возвращал True
        screen.command_registry.execute_command = Mock(return_value=True)
        mock_key = 97 # ord('a')

        # Вызов тестируемого метода
        screen.handle_input(mock_key)

        # Проверки
        screen.command_registry.execute_command.assert_called_once_with(mock_key, screen)

    def test_handle_input_with_unregistered_command(self) -> None:
        """Тест handle_input при нажатии клавиши без зарегистрированной команды."""
        # Создание экземпляра
        screen = self.ConcreteBaseScreen(self.mock_screen_manager)

        # Настройка моков после создания экземпляра
        # Мокаем execute_command так, чтобы он возвращал False
        screen.command_registry.execute_command = Mock(return_value=False)
        mock_key = 98 # ord('b')
        
        # Заменяем _handle_unregistered_key на мок
        screen._handle_unregistered_key = Mock() # type: ignore[method-assign]

        # Вызов тестируемого метода
        screen.handle_input(mock_key)

        # Проверки
        screen.command_registry.execute_command.assert_called_once_with(mock_key, screen)
        screen._handle_unregistered_key.assert_called_once_with(mock_key) # type: ignore[attr-defined]

    # def test_render_draws_elements_and_refreshes(self) -> None:
    #     """Тест отрисовки экрана."""
    #     # Создание экземпляра
    #     screen = self.ConcreteBaseScreen(self.mock_screen_manager)
    #
    #     # Настройка элементов для отрисовки
    #     mock_element1 = Mock()
    #     mock_element2 = Mock()
    #     screen.elements = [mock_element1, mock_element2]
    #
    #     # Создаем мок stdscr
    #     mock_stdscr = Mock()
    #
    #     # Вызов тестируемого метода
    #     screen.render(mock_stdscr)
    #
    #     # Проверки
    #     self.mock_renderer.clear.assert_called_once()
    #     # Проверяем, что render был вызван на каждом элементе с renderer
    #     mock_element1.render.assert_called_once_with(self.mock_renderer)
    #     mock_element2.render.assert_called_once_with(self.mock_renderer)
    #     # Проверяем, что refresh был вызван у renderer
    #     self.mock_renderer.refresh.assert_called_once()


if __name__ == '__main__':
    unittest.main()