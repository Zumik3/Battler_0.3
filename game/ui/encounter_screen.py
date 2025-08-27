# game/ui/encounter_screen.py
"""Универсальный экран для отображения событий похода (Encounter)."""
import curses
from typing import TYPE_CHECKING, Dict

from game.events.combat import LogUpdatedEvent
from game.events.event import Event
from game.mixins.ui_mixin import StandardLayoutMixin
from game.ui.base_screen import BaseScreen
from game.ui.components.battle_components import PlayerGroupPanel, EnemyGroupPanel, BattleLog
from game.systems.encounters.events import BattleEncounterEvent

if TYPE_CHECKING:
    from game.ui.screen_manager import ScreenManager
    from game.systems.encounters.events import EncounterEvent


class EncounterScreen(BaseScreen, StandardLayoutMixin):
    """Экран для отображения и взаимодействия с событиями похода."""

    # --- Константы для макета ---
    HEADER_HEIGHT = 2
    UNITS_HEIGHT = 5
    FOOTER_Y_OFFSET = 2
    HORIZONTAL_MARGIN = 1
    GROUPS_GAP = 1
    MIN_LOG_HEIGHT = 3
    MIN_LOG_WIDTH = 10
    # --- Конец констант ---

    def __init__(self, manager: 'ScreenManager'):
        
        self.encounter_manager = manager.game_manager.encounter_manager

        if self.encounter_manager.current_encounter:
            self.current_event = self.encounter_manager.current_encounter.events[self.encounter_manager.current_event_index]

        super().__init__(manager)
        # Инициализация панелей
        self.left_panel: PlayerGroupPanel | None = None
        self.right_panel: EnemyGroupPanel | None = None
        self.event_log: BattleLog | None = None
        
        # Получаем текущее событие
        
        # self.current_event: 'EncounterEvent' | None = self.encounter_manager.current_encounter.events[self.encounter_manager.current_event_index] if self.encounter_manager.current_encounter else None

        self._setup_event_listeners()
        self._setup_elements() # Переносим вызов сюда, чтобы self.current_event был доступен

    def _setup_event_listeners(self) -> None:
        """Настраивает обработчики событий."""
        event_bus = self.manager.game_manager.event_bus
        event_bus.subscribe(None, LogUpdatedEvent, self._on_log_update_event)
        
    def _on_log_update_event(self, event: Event) -> None:
        """Обработчик событий обновления лога."""
        self.render(self.renderer.stdscr)
        
    def _recalculate_layout(self, screen_width: int, screen_height: int) -> Dict[str, Dict[str, int]]:
        """Пересчитывает размеры и позиции компонентов."""
        units_y = self.HEADER_HEIGHT
        total_units_width = max(0, screen_width - 2 * self.HORIZONTAL_MARGIN - self.GROUPS_GAP)
        half_width = total_units_width // 2
        left_panel_width = half_width
        right_panel_width = total_units_width - left_panel_width
        left_panel_x = self.HORIZONTAL_MARGIN
        right_panel_x = left_panel_x + left_panel_width + self.GROUPS_GAP

        log_x = 0
        log_y = units_y + self.UNITS_HEIGHT
        log_width = max(self.MIN_LOG_WIDTH, screen_width)
        available_height = screen_height - log_y - self.FOOTER_Y_OFFSET
        log_height = max(self.MIN_LOG_HEIGHT, available_height)

        return {
            'left_panel': {'x': left_panel_x, 'y': units_y, 'width': left_panel_width, 'height': self.UNITS_HEIGHT},
            'right_panel': {'x': right_panel_x, 'y': units_y, 'width': right_panel_width, 'height': self.UNITS_HEIGHT},
            'event_log': {'x': log_x, 'y': log_y, 'width': log_width, 'height': log_height}
        }

    def _setup_elements(self) -> None:
        """Настройка элементов экрана в зависимости от типа события."""
        self.elements = []

        if isinstance(self.current_event, BattleEncounterEvent):
            self._setup_battle_elements()
        else:
            # TODO: Обработка других типов событий (диалоги, сундуки и т.д.)
            pass

    def _setup_battle_elements(self) -> None:
        """Настройка элементов для события боя."""
        from game.game_manager import get_game_manager
        game_manager = get_game_manager()
        player_data = game_manager.get_player_group()
        enemy_data = game_manager.get_current_enemies()

        screen_width = self.renderer.width if self.renderer else 80
        screen_height = self.renderer.height if self.renderer else 24

        layout = self._recalculate_layout(screen_width, screen_height)

        self.left_panel = PlayerGroupPanel(
            x=layout['left_panel']['x'], y=layout['left_panel']['y'],
            width=layout['left_panel']['width'], height=layout['left_panel']['height'],
            players=player_data
        )

        self.right_panel = EnemyGroupPanel(
            x=layout['right_panel']['x'], y=layout['right_panel']['y'],
            width=layout['right_panel']['width'], height=layout['right_panel']['height'],
            enemies=enemy_data
        )

        self.event_log = BattleLog(
            x=layout['event_log']['x'], y=layout['event_log']['y'],
            width=layout['event_log']['width'], height=layout['event_log']['height']
        )
        
        # Настройка контроллера лога
        self.manager.game_manager.battle_manager.setup_battle_log_controller(
            event_bus=self.manager.game_manager.event_bus, 
            battle_log=self.event_log
        )

    def _update_component_sizes(self) -> None:
        """Обновление размеров компонентов."""
        if not self.renderer: return

        screen_width, screen_height = self.renderer.width, self.renderer.height
        layout = self._recalculate_layout(screen_width, screen_height)

        if self.left_panel:
            self.left_panel.x, self.left_panel.y = layout['left_panel']['x'], layout['left_panel']['y']
            self.left_panel.width, self.left_panel.height = layout['left_panel']['width'], layout['left_panel']['height']
            self.left_panel._update_panels()

        if self.right_panel:
            self.right_panel.x, self.right_panel.y = layout['right_panel']['x'], layout['right_panel']['y']
            self.right_panel.width, self.right_panel.height = layout['right_panel']['width'], layout['right_panel']['height']
            self.right_panel._update_panels()

        if self.event_log:
            self.event_log.x, self.event_log.y = layout['event_log']['x'], layout['event_log']['y']
            self.event_log.width, self.event_log.height = layout['event_log']['width'], layout['event_log']['height']

    def _setup_commands(self) -> None:
        """Настройка команд в зависимости от типа события."""
        # self.command_registry.clear()

        if isinstance(self.current_event, BattleEncounterEvent):
            from game.ui.commands.battle_commands import AttackCommand, DefendCommand, MagicCommand
            from game.ui.commands.common_commands import OpenInventoryCommand, GoBackCommand

            self.add_command(AttackCommand())
            self.add_command(DefendCommand())
            self.add_command(MagicCommand())
            self.add_command(OpenInventoryCommand())
            self.add_command(GoBackCommand())
        else:
            # TODO: Зарегистрировать команды для других типов событий
            from game.ui.commands.common_commands import GoBackCommand
            self.add_command(GoBackCommand())

    def render(self, stdscr: curses.window) -> None:
        """Отрисовка экрана."""
        self._update_component_sizes()
        self.renderer.clear()
        self.render_standard_layout("=== ПОХОД ===")

        if self.left_panel: self.left_panel.render(self.renderer)
        if self.right_panel: self.right_panel.render(self.renderer)
        if self.event_log: self.event_log.render(self.renderer)
        
        self.renderer.refresh()

    def _handle_unregistered_key(self, key: int) -> None:
        """Обработка незарегистрированных клавиш."""
        if key == curses.KEY_UP:
            if self.event_log: self.event_log.scroll_up()
        elif key == curses.KEY_DOWN:
            if self.event_log: self.event_log.scroll_down()