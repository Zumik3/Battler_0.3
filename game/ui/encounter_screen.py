# game/ui/encounter_screen.py
"""Универсальный экран для отображения событий похода (Encounter)."""
import curses
from typing import TYPE_CHECKING, Dict

from game.events.battle_events import BattleEndedEvent
from game.events.combat import LogUpdatedEvent
from game.events.encounter_events import RoomSequenceCompletedEvent
from game.events.event import Event
from game.mixins.ui_mixin import StandardLayoutMixin
from game.ui.base_screen import BaseScreen
from game.ui.command_system.command import LambdaCommand
from game.ui.components.battle_components import PlayerGroupPanel, EnemyGroupPanel, BattleLog
from game.events.render_data import RenderData
from game.ui.rendering.color_manager import Color
from game.ui.rendering.render_data_builder import RenderDataBuilder

if TYPE_CHECKING:
    from game.ui.screen_manager import ScreenManager


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
        self.state = "BATTLE"

        # Создаем врагов для ПЕРВОЙ комнаты до инициализации UI, чтобы
        # панели сразу отрисовались с нужными данными.
        current_event = self.encounter_manager.get_current_event()
        if current_event and hasattr(current_event, 'enemies'):
            manager.game_manager.create_enemies(
                enemy_data_list=current_event.enemies,
                game_context=manager.game_manager.context
            )

        self.left_panel: PlayerGroupPanel | None = None
        self.right_panel: EnemyGroupPanel | None = None
        self.event_log: BattleLog | None = None

        super().__init__(manager)
        self._setup_event_listeners()

    def _refresh_panel_data(self) -> None:
        """Обновляет данные в панелях из game_manager."""
        if not self.manager or not self.manager.game_manager:
            return

        game_manager = self.manager.game_manager

        if self.left_panel:
            player_data = game_manager.get_player_group()
            self.left_panel.update_players(player_data)

        if self.right_panel:
            enemy_data = game_manager.get_current_enemies()
            self.right_panel.update_enemies(enemy_data)

    def on_enter(self) -> None:
        """Вызывается при переключении на этот экран."""
        if self.encounter_manager.current_encounter:
            encounter_description = self.encounter_manager.current_encounter.description
            if self.event_log:
                self.event_log.add_message(RenderData(template=encounter_description, replacements={}))
        
        # Враги для первой комнаты уже созданы в __init__.
        # Просто запускаем бой.
        self.state = "BATTLE"
        self._setup_commands()
        
        if self.encounter_manager.current_encounter:
            self.encounter_manager.start_encounter(self.encounter_manager.current_encounter)
        
        # Первая отрисовка происходит в ScreenManager после on_enter,
        # но на всякий случай можно вызвать и здесь, если нужно.
        # self.render(self.renderer.stdscr)

    def _setup_event_listeners(self) -> None:
        """Настраивает обработчики событий."""
        event_bus = self.manager.game_manager.event_bus
        event_bus.subscribe(None, LogUpdatedEvent, self._on_log_update_event)
        event_bus.subscribe(None, BattleEndedEvent, self._on_battle_ended)
        event_bus.subscribe(None, RoomSequenceCompletedEvent, self._on_sequence_completed)

    def _on_log_update_event(self, event: Event) -> None:
        """Обработчик событий обновления лога."""
        self.render(self.renderer.stdscr)

    def _on_battle_ended(self, event: BattleEndedEvent) -> None:
        """Обработчик события завершения боя."""
        if event.result and event.result.alive_players:
            if self.state == "SEQUENCE_COMPLETE":
                return

            self.state = "VICTORY"
            # if self.event_log:
            #     self.event_log.add_message(RenderData(template="Комната зачищена! Нажмите Enter, чтобы пройти в следующую.", replacements={}))
            self._setup_commands()

        else:
            self.state = "BATTLE_LOST"
            # if self.event_log:
            #     self.event_log.add_message(RenderData(template="Поражение... Нажмите Enter, чтобы выйти.", replacements={}))
            self._setup_commands()
        
        self.render(self.renderer.stdscr)

    def _on_sequence_completed(self, event: RoomSequenceCompletedEvent) -> None:
        """Обработчик завершения всей последовательности комнат."""
        self.state = "SEQUENCE_COMPLETE"
        if self.event_log:
            if event.success:
                result_text = "Победа"
                result_color = Color.GREEN
            else:
                result_text = "Поражение"
            result_color = Color.RED

            message_data = (RenderDataBuilder()
                .add_text("Поход завершен! Результат: ")
                .add_styled_text(result_text, color=result_color, bold=True)
                .add_text(". Нажмите Enter, чтобы выйти.")
                .build())

            #message = f"Поход завершен! Результат: {'Победа' if event.success else 'Поражение'}. Нажмите Enter, чтобы выйти."
            self.event_log.add_message(message_data)
        self._setup_commands()
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
        """Настройка элементов экрана."""
        self.elements = []
        self._setup_battle_elements()

    def _setup_battle_elements(self) -> None:
        """Настройка элементов для события боя."""
        game_manager = self.manager.game_manager
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
        """Настройка команд в зависимости от состояния экрана."""
        self.command_registry.clear()

        if self.state == "VICTORY":
            self.add_command(LambdaCommand(
                name="Продолжить",
                description="Перейти в следующую комнату",
                keys=[10, curses.KEY_ENTER],
                display_key="Enter",
                action=lambda context: self._prepare_next_room()
            ))
        elif self.state in ["SEQUENCE_COMPLETE", "BATTLE_LOST"]:
            self.add_command(LambdaCommand(
                name="Завершить",
                description="Вернуться в главное меню",
                keys=[10, curses.KEY_ENTER],
                display_key="Enter",
                action=lambda context: self.manager.change_screen("main")
            ))

    def _prepare_next_room(self) -> None:
        """Готовит переход в следующую комнату."""
        if self.encounter_manager.advance_to_next_room():
            self._setup_new_room()
            self.state = "BATTLE"
            self._setup_commands()
            
            self.encounter_manager._execute_current_event()
            self.render(self.renderer.stdscr)

    def _setup_new_room(self) -> None:
        """Настраивает новую комнату, создавая врагов."""
        current_event = self.encounter_manager.get_current_event()
        if current_event and hasattr(current_event, 'enemies'):
            self.manager.game_manager.create_enemies(
                enemy_data_list=current_event.enemies,
                game_context=self.manager.game_manager.context
            )
            self._refresh_panel_data()

    def render(self, stdscr: curses.window) -> None:
        """Отрисовка экрана."""
        self._refresh_panel_data()
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
