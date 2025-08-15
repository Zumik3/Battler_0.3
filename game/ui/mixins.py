# game/ui/mixins.py
"""
Миксины для повторно используемой функциональности экранов.
"""
from typing import TYPE_CHECKING, Protocol

from game.ui.rendering.renderable import Text, Separator
from game.ui.rendering.color_manager import Color
from game.ui.command_system import CommandRenderer

if TYPE_CHECKING:
    from game.ui.base_screen import BaseScreen
    from game.ui.rendering.renderer import Renderer
    from game.ui.command_system.command import CommandRegistry

# Протокол, описывающий интерфейс для классов, использующих миксины
class LayoutProtocol(Protocol):
    """Протокол для классов с методами отрисовки шапки и подвала."""
    renderer: 'Renderer' # type: ignore # Будет определен в BaseScreen
    command_registry: 'CommandRegistry' # type: ignore # Будет определен в BaseScreen

    def render_header(self, title: str) -> None: ...
    def render_footer(self) -> None: ...



class HeaderMixin:
    """Миксин для отрисовки стандартной шапки экрана."""
    
    def render_header(self: LayoutProtocol, title: str) -> None:
        """
        Отрисовка стандартной шапки экрана.
        Args:
            title: Текст заголовка.
        """
        # Центрируем заголовок
        # Используем getattr для доступа к атрибутам через протокол
        renderer = getattr(self, 'renderer')
        title_x = max(0, (renderer.width - len(title)) // 2)
        header_text = Text(title, title_x, 0, bold=True, color=Color.CYAN)
        header_text.render(renderer)

        # Рисуем разделитель под заголовком
        header_separator = Separator(1, color=Color.DEFAULT)
        header_separator.render(renderer)


class FooterMixin:
    """Миксин для отрисовки стандартного подвала экрана."""
    
    def render_footer(self: LayoutProtocol) -> None:
        """
        Отрисовка стандартного подвала экрана.
        Получает команды из command_registry и отрисовывает их.
        """
        # Получаем команды для отрисовки
        command_registry = getattr(self, 'command_registry')
        renderer = getattr(self, 'renderer')
        commands = command_registry.get_all_commands()

        # Рассчитываем позиции подвала
        footer_separator_y = max(0, renderer.height - 2)
        commands_y = max(0, renderer.height - 1)
        
        # Отрисовка разделителя подвала
        footer_separator = Separator(footer_separator_y, color=Color.GRAY)
        footer_separator.render(renderer)

        # Отрисовка команд в последней строке
        footer_command_renderer = CommandRenderer(y=commands_y)
        command_elements = footer_command_renderer.render_commands(commands)
        for element in command_elements:
            element.render(renderer)


# Можно также создать комбинированный миксин для удобства
class StandardLayoutMixin(HeaderMixin, FooterMixin):
    """Миксин, объединяющий стандартную шапку и подвал."""
    
    def render_standard_layout(self: LayoutProtocol, title: str) -> None:
        """
        Отрисовка стандартного макета экрана (шапка + подвал).
        Args:
            title: Текст заголовка.
        """
        # Теперь mypy знает, что у self есть эти методы благодаря LayoutProtocol
        self.render_header(title)
        self.render_footer()
