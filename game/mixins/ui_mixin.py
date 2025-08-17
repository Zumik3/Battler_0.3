# game/mixins/ui_mixin.py
"""Миксины для UI функциональности."""

from typing import TYPE_CHECKING, Protocol

from game.ui.command_system import CommandRenderer
from game.ui.rendering.color_manager import Color
from game.ui.rendering.renderable import Separator, Text

if TYPE_CHECKING:
    from game.ui.base_screen import BaseScreen
    from game.ui.command_system.command import CommandRegistry
    from game.ui.rendering.renderer import Renderer


class LayoutProtocol(Protocol):
    """Протокол для классов с методами отрисовки шапки и подвала."""
    renderer: 'Renderer'
    command_registry: 'CommandRegistry'

    def render_header(self, title: str) -> None: ...
    def render_footer(self) -> None: ...


class HeaderMixin:
    """Миксин для отрисовки стандартной шапки экрана."""

    def render_header(self: LayoutProtocol, title: str) -> None:
        """
        Отрисовка стандартной шапки экрана.
        """
        renderer = getattr(self, 'renderer')
        title_x = max(0, (renderer.width - len(title)) // 2)
        header_text = Text(title, title_x, 0, bold=True, color=Color.CYAN)
        header_text.render(renderer)

        header_separator = Separator(1, color=Color.DEFAULT)
        header_separator.render(renderer)


class FooterMixin:
    """Миксин для отрисовки стандартного подвала экрана."""

    def render_footer(self: LayoutProtocol) -> None:
        """
        Отрисовка стандартного подвала экрана.
        """
        command_registry = getattr(self, 'command_registry')
        renderer = getattr(self, 'renderer')
        commands = command_registry.get_all_commands()

        footer_separator_y = max(0, renderer.height - 2)
        commands_y = max(0, renderer.height - 1)

        footer_separator = Separator(footer_separator_y, color=Color.GRAY)
        footer_separator.render(renderer)

        footer_command_renderer = CommandRenderer(y=commands_y)
        command_elements = footer_command_renderer.render_commands(commands)
        for element in command_elements:
            element.render(renderer)


class StandardLayoutMixin(HeaderMixin, FooterMixin):
    """Миксин, объединяющий стандартную шапку и подвал."""

    def render_standard_layout(self: LayoutProtocol, title: str) -> None:
        """
        Отрисовка стандартного макета экрана.
        """
        self.render_header(title)
        self.render_footer()