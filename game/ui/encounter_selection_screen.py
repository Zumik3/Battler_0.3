# game/ui/encounter_selection_screen.py
"""Экран для выбора похода."""

import curses
from typing import TYPE_CHECKING

from game.ui.base_screen import BaseScreen
from game.ui.rendering.renderable import Text
from game.ui.rendering.color_manager import Color
from game.ui.command_system.command import LambdaCommand
from game.ui.commands.common_commands import GoBackCommand
from game.ui.command_system.command_renderer import CommandRenderer

if TYPE_CHECKING:
    from game.ui.screen_manager import ScreenManager

class EncounterSelectionScreen(BaseScreen):
    """Экран для выбора одного из нескольких сгенерированных походов."""

    def __init__(self, manager: 'ScreenManager'):
        self.encounter_manager = manager.game_manager.encounter_manager
        self.encounters = self.encounter_manager.generate_encounters()
        super().__init__(manager)

    def _setup_elements(self) -> None:
        """Настройка элементов экрана."""
        self.elements = []
        y_offset = 2

        if not self.encounters:
            self.elements.append(Text("Нет доступных походов.", 2, y_offset, color=Color.YELLOW))
            return

        for i, encounter in enumerate(self.encounters):
            self.elements.append(Text(f"[{i + 1}] {encounter.name} ({encounter.difficulty})", 2, y_offset, bold=True))
            self.elements.append(Text(f"    {encounter.description}", 2, y_offset + 1, dim=True))
            y_offset += 3

    def _setup_commands(self) -> None:
        """Настройка команд экрана."""
        # self.command_registry.clear()

        for i, encounter in enumerate(self.encounters):
            def create_action(enc):
                def action(context):
                    if context:
                        context.encounter_manager.init_encounter(enc)
                        context.manager.change_screen("encounter")
                    
                return action

            self.add_command(
                LambdaCommand(
                    name=f"Выбрать {i + 1}",
                    description=f"Начать поход '{encounter.name}'",
                    keys=[str(i + 1)],
                    action=create_action(encounter)
                )
            )

        self.add_command(GoBackCommand())

    def render(self, stdscr: curses.window) -> None:
        """Отрисовка экрана."""
        self.renderer.clear()
        
        # Ручная отрисовка заголовка
        title = "=== ВЫБОР ПОХОДА ==="
        title_x = max(0, (self.renderer.width - len(title)) // 2)
        self.renderer.draw_text(title, title_x, 0, bold=True, color=Color.CYAN)
        
        for element in self.elements:
            element.render(self.renderer)
            
        # Ручная отрисовка подвала с командами
        commands = self.command_registry.get_all_commands()
        footer_y = self.renderer.height - 1
        command_renderer = CommandRenderer(y=footer_y)
        command_elements = command_renderer.render_commands(commands)
        for element in command_elements:
            element.render(self.renderer)

        self.renderer.refresh()