# tests/test_ui/test_mixins.py
"""Тесты для миксинов UI."""

import unittest
from unittest.mock import Mock, patch

# Предполагаем, что LayoutProtocol импортируется отсюда
from game.ui.mixins import FooterMixin, HeaderMixin, LayoutProtocol, StandardLayoutMixin
from game.ui.rendering.color_manager import Color


# Явно наследуем от LayoutProtocol
class _TestLayoutProtocol(LayoutProtocol):
    """Тестовая реализация LayoutProtocol для миксинов."""

    def __init__(self) -> None:
        """Инициализация тестового протокола."""
        # Инициализируем атрибуты, ожидаемые LayoutProtocol
        # Используем Mock для имитации реальных объектов
        self.renderer: Mock = Mock() 
        self.command_registry: Mock = Mock()
        # Явно указываем типы атрибутов, чтобы mypy знал, что они существуют
        # Типы Mock подойдут, так как они будут иметь необходимые атрибуты во время теста

    # Заглушки для абстрактных методов протокола, чтобы mypy не считал класс абстрактным
    def render_header(self, title: str) -> None:
        pass

    def render_footer(self) -> None:
        pass


class HeaderMixinTest(unittest.TestCase):
    """Тесты для HeaderMixin."""

    def setUp(self) -> None:
        """Настройка тестового окружения."""
        # Теперь TestHeaderClass наследуется от HeaderMixin и _TestLayoutProtocol,
        # который реализует LayoutProtocol. MyPy должен принять это.
        class TestHeaderClass(HeaderMixin, _TestLayoutProtocol):
            pass

        # mypy думает, что TestHeaderClass абстрактный из-за нереализованных методов протокола
        # Но для тестирования миксина это приемлемо
        self.test_instance = TestHeaderClass()  # type: ignore
        # Настройка моков
        self.test_instance.renderer.width = 20
        self.test_instance.renderer.height = 10

    @patch('game.ui.mixins.Text')
    @patch('game.ui.mixins.Separator')
    def test_render_header(self, mock_separator, mock_text) -> None:
        """Тест отрисовки заголовка."""
        title = "Test Title"

        # Этот вызов теперь должен пройти проверку mypy
        self.test_instance.render_header(title)
        
        # Проверяем, что Text был создан с правильными параметрами
        mock_text.assert_called_once_with(
            title, 5, 0, bold=True, color=Color.CYAN
        )
        
        # Проверяем, что render был вызван у текста
        mock_text.return_value.render.assert_called_once_with(
            self.test_instance.renderer
        )
        
        # Проверяем, что Separator был создан и отрисован
        mock_separator.assert_called_once_with(1, color=Color.DEFAULT)
        mock_separator.return_value.render.assert_called_once_with(
            self.test_instance.renderer
        )

    @patch('game.ui.mixins.Text')
    @patch('game.ui.mixins.Separator')
    def test_render_header_centering_with_short_title(self, mock_separator, mock_text) -> None:
        """Тест центрирования короткого заголовка."""
        title = "A"
        self.test_instance.renderer.width = 20

        self.test_instance.render_header(title)

        # Заголовок должен быть центрирован: (20 - 1) // 2 = 9
        mock_text.assert_called_once_with(
            title, 9, 0, bold=True, color=Color.CYAN
        )

    @patch('game.ui.mixins.Text')
    @patch('game.ui.mixins.Separator')
    def test_render_header_centering_with_long_title(self, mock_separator, mock_text) -> None:
        """Тест центрирования длинного заголовка."""
        title = "Very Long Title That Exceeds Width"
        self.test_instance.renderer.width = 20

        self.test_instance.render_header(title)

        # При отрицательном значении x должен быть 0
        mock_text.assert_called_once_with(
            title, 0, 0, bold=True, color=Color.CYAN
        )


class FooterMixinTest(unittest.TestCase):
    """Тесты для FooterMixin."""

    def setUp(self) -> None:
        """Настройка тестового окружения."""
        class TestFooterClass(FooterMixin, _TestLayoutProtocol):
            pass

        self.test_instance = TestFooterClass()  # type: ignore
        self.test_instance.renderer.width = 20
        self.test_instance.renderer.height = 10

        # Мокаем команды
        self.mock_commands = [Mock(), Mock()]
        self.test_instance.command_registry.get_all_commands.return_value = self.mock_commands

    @patch('game.ui.mixins.Separator')
    @patch('game.ui.mixins.CommandRenderer')
    def test_render_footer(self, mock_command_renderer, mock_separator) -> None:
        """Тест отрисовки подвала."""
        # Настраиваем моки
        mock_command_elements = [Mock(), Mock()]
        mock_command_renderer_instance = mock_command_renderer.return_value
        mock_command_renderer_instance.render_commands.return_value = mock_command_elements

        self.test_instance.render_footer()

        # Проверяем вызов get_all_commands
        self.test_instance.command_registry.get_all_commands.assert_called_once()

        # Проверяем создание и отрисовку разделителя подвала
        mock_separator.assert_called_once_with(8, color=Color.GRAY)
        mock_separator.return_value.render.assert_called_once_with(
            self.test_instance.renderer
        )

        # Проверяем создание CommandRenderer
        mock_command_renderer.assert_called_once_with(y=9)

        # Проверяем вызов render_commands
        mock_command_renderer_instance.render_commands.assert_called_once_with(
            self.mock_commands
        )

        # Проверяем, что render был вызван у каждого элемента команд
        for element in mock_command_elements:
            element.render.assert_called_once_with(self.test_instance.renderer)

    @patch('game.ui.mixins.Separator')
    @patch('game.ui.mixins.CommandRenderer')
    def test_render_footer_with_small_height(self, mock_command_renderer, mock_separator) -> None:
        """Тест отрисовки подвала при малой высоте."""
        self.test_instance.renderer.height = 1

        # Настраиваем моки
        mock_command_elements = [Mock()]
        mock_command_renderer_instance = mock_command_renderer.return_value
        mock_command_renderer_instance.render_commands.return_value = mock_command_elements

        self.test_instance.render_footer()

        # При высоте 1: footer_separator_y = max(0, 1-2) = 0, commands_y = max(0, 1-1) = 0
        mock_separator.assert_called_once_with(0, color=Color.GRAY)
        mock_command_renderer.assert_called_once_with(y=0)


class StandardLayoutMixinTest(unittest.TestCase):
    """Тесты для StandardLayoutMixin."""

    def setUp(self) -> None:
        """Настройка тестового окружения."""
        class TestStandardLayoutClass(StandardLayoutMixin, _TestLayoutProtocol):
            pass

        self.test_instance = TestStandardLayoutClass()  # type: ignore
        self.test_instance.renderer.width = 20
        self.test_instance.renderer.height = 10

    @patch('game.ui.mixins.Text')
    @patch('game.ui.mixins.Separator')
    @patch('game.ui.mixins.CommandRenderer')
    def test_render_standard_layout(self, mock_command_renderer, mock_separator, mock_text) -> None:
        """Тест отрисовки стандартного макета."""
        # Настраиваем моки для подвала
        mock_command_elements = [Mock()]
        mock_command_renderer_instance = mock_command_renderer.return_value
        mock_command_renderer_instance.render_commands.return_value = mock_command_elements
        self.test_instance.command_registry.get_all_commands.return_value = [Mock()]

        title = "Standard Layout"  # Длина 14 символов
        expected_x = max(0, (self.test_instance.renderer.width - len(title)) // 2)  # 20 - 14 = 6 // 2 = 3

        self.test_instance.render_standard_layout(title)

        # Проверяем вызов render_header - используем вычисленное значение expected_x
        mock_text.assert_called_once_with(
            title, expected_x, 0, bold=True, color=Color.CYAN
        )
        mock_text.return_value.render.assert_called_once_with(
            self.test_instance.renderer
        )

        # Проверяем, что были вызваны оба разделителя (один из header, один из footer)
        self.assertEqual(mock_separator.call_count, 2)

        # Проверяем вызов CommandRenderer
        mock_command_renderer.assert_called_once_with(y=9)


if __name__ == '__main__':
    unittest.main()
