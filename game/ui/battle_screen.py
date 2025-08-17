# game/ui/battle_screen.py
"""Экран боя.
Отображает боевую сцену с возможностью взаимодействия."""
import curses
from typing import TYPE_CHECKING, Dict, Any, Optional, List, Tuple

# - ДОБАВЛЯЕМ ИМПОРТ МИКСИНА -
from game.mixins.ui_mixin import StandardLayoutMixin
# -
from game.ui.base_screen import BaseScreen
from game.ui.rendering.color_manager import Color
from game.ui.rendering.renderable import Text, Separator
# - ИМПОРТИРУЕМ НОВЫЕ КОМПОНЕНТЫ -
from game.ui.components.battle_components import (PlayerGroupPanel, EnemyGroupPanel, BattleLog)
# -
from game.ui.base_screen import BaseScreen
from game.ui.rendering.color_manager import Color
# Импортируем get_game_manager для использования внутри _setup_elements
from game.game_manager import get_game_manager

# - ДОБАВЛЯЕМ ИМПОРТ ДЛЯ TYPE_CHECKING -
if TYPE_CHECKING:
    from game.ui.screen_manager import ScreenManager
    from game.entities.player import Player
    from game.entities.monster import Monster
    from game.ui.rendering.renderer import Renderer
# ---


class BattleScreen(BaseScreen, StandardLayoutMixin):
    """Экран боя."""

    # --- Константы для макета ---
    HEADER_HEIGHT = 2
    #UNITS_Y_OFFSET = 1 # Отступ блока юнитов от заголовка
    UNITS_HEIGHT = 5 # Фиксированная высота блока юнитов
    #LOG_Y_OFFSET = 1 # Отступ лога от блока юнитов
    FOOTER_Y_OFFSET = 2 # Отступ подвала от низа лога
    HORIZONTAL_MARGIN = 1 # Отступы слева и справа
    GROUPS_GAP = 1 # Зазор между группами игроков и врагов
    MIN_LOG_HEIGHT = 3 # Минимальная высота лога
    MIN_LOG_WIDTH = 10 # Минимальная ширина лога
    # --- Конец констант ---

    def __init__(self, manager: 'ScreenManager'):
        # Инициализируем атрибуты для компонентов
        # Они будут инициализированы в _setup_elements
        self.player_group: Optional[PlayerGroupPanel] = None
        self.enemy_group: Optional[EnemyGroupPanel] = None
        self.battle_log: Optional[BattleLog] = None
        # Вызываем родительский конструктор
        # _setup_elements будет вызван внутри него
        super().__init__(manager)

    def _recalculate_layout(self, screen_width: int, screen_height: int) -> Dict[str, Dict[str, int]]:
        """
        Пересчитывает размеры и позиции всех основных компонентов экрана боя.

        Args:
            screen_width: Текущая ширина экрана.
            screen_height: Текущая высота экрана.

        Returns:
            Словарь с ключами 'player_group', 'enemy_group', 'battle_log',
            каждый из которых содержит словарь {'x', 'y', 'width', 'height'}.
        """
        # --- Размеры и позиции ---
        units_y = self.HEADER_HEIGHT #+ self.UNITS_Y_OFFSET

        # --- Расчет ширины для панелей юнитов ---
        # Доступная ширина для блоков юнитов (учитываем отступы и зазор)
        total_units_width = max(
            0,
            screen_width - 2 * self.HORIZONTAL_MARGIN - self.GROUPS_GAP
        )

        # Делим ширину пополам между игроками и монстрами
        half_width = total_units_width // 2
        player_group_width = half_width
        enemy_group_width = total_units_width - player_group_width

        # Координаты X
        player_group_x = self.HORIZONTAL_MARGIN
        enemy_group_x = player_group_x + player_group_width + self.GROUPS_GAP

        # --- Размеры и позиции лога боя ---
        log_x = 0  # self.HORIZONTAL_MARGIN
        log_y = units_y + self.UNITS_HEIGHT #+ self.LOG_Y_OFFSET
        log_width = max(self.MIN_LOG_WIDTH, screen_width * self.HORIZONTAL_MARGIN)

        # Высота лога - всё оставшееся пространство минус отступы и подвал
        available_height = screen_height - log_y - self.FOOTER_Y_OFFSET
        log_height = max(self.MIN_LOG_HEIGHT, available_height)

        return {
            'player_group': {
                'x': player_group_x,
                'y': units_y,
                'width': player_group_width,
                'height': self.UNITS_HEIGHT
            },
            'enemy_group': {
                'x': enemy_group_x,
                'y': units_y,
                'width': enemy_group_width,
                'height': self.UNITS_HEIGHT
            },
            'battle_log': {
                'x': log_x,
                'y': log_y,
                'width': log_width,
                'height': log_height
            }
        }

    def _setup_elements(self) -> None:
        """Настройка элементов экрана."""
        self.elements = [] # Очищаем список, так как компоненты будут отрисовываться напрямую

        # - ПОЛУЧАЕМ ДАННЫЕ ИЗ GameManager НЕПОСРЕДСТВЕННО В _setup_elements -
        # Это решает проблему порядка инициализации
        game_manager = get_game_manager()
        real_enemy_data = game_manager.get_current_enemies()
        real_player_data = game_manager.get_player_group()
        # -

        # Получаем начальные размеры экрана из рендерера
        if self.renderer:
            screen_width = self.renderer.width
            screen_height = self.renderer.height
        else:
            # fallback значения, если renderer еще не готов
            # Используем значения из конфигурации, если они доступны
            try:
                from game.config import get_config
                config = get_config()
                screen_width = config.ui.screen_width
                screen_height = config.ui.screen_height
            except Exception:
                screen_width = 80
                screen_height = 24

        # --- ИСПОЛЬЗУЕМ ОБЩУЮ ЛОГИКУ РАСЧЕТА ---
        layout = self._recalculate_layout(screen_width, screen_height)

        # Создаем панели с рассчитанными размерами
        self.player_group = PlayerGroupPanel(
            x=layout['player_group']['x'],
            y=layout['player_group']['y'],
            width=layout['player_group']['width'],
            height=layout['player_group']['height'],
            players=real_player_data  # Передаем данные игроков
        )

        self.enemy_group = EnemyGroupPanel(
            x=layout['enemy_group']['x'],
            y=layout['enemy_group']['y'],
            width=layout['enemy_group']['width'],
            height=layout['enemy_group']['height'],
            enemies=real_enemy_data  # Передаем данные врагов
        )

        # Инициализируем лог боя
        self.battle_log = BattleLog(
            x=layout['battle_log']['x'],
            y=layout['battle_log']['y'],
            width=layout['battle_log']['width'],
            height=layout['battle_log']['height']
        )
        # Добавляем тестовые сообщения в лог
        # TODO: Заменить на реальные сообщения из игровой логики
        self.battle_log.add_message("Битва начинается!")
        # ---

    def _update_component_sizes(self) -> None:
        """Обновление размеров компонентов."""
        if not self.renderer:
            return

        # Получаем текущие размеры экрана
        screen_width = self.renderer.width
        screen_height = self.renderer.height

        # --- ИСПОЛЬЗУЕМ ОБЩУЮ ЛОГИКУ РАСЧЕТА ---
        layout = self._recalculate_layout(screen_width, screen_height)
        # ---

        # Обновляем размеры и позиции панелей групп
        if self.player_group:
            self.player_group.x = layout['player_group']['x']
            self.player_group.y = layout['player_group']['y'] # Обновляем Y тоже
            self.player_group.width = layout['player_group']['width']
            self.player_group.height = layout['player_group']['height']
            # Обновляем размеры дочерних компонентов групп
            # _update_panels будет использовать новые self.x, self.width
            self.player_group._update_panels() 

        if self.enemy_group:
            self.enemy_group.x = layout['enemy_group']['x']
            self.enemy_group.y = layout['enemy_group']['y'] # Обновляем Y тоже
            self.enemy_group.width = layout['enemy_group']['width']
            self.enemy_group.height = layout['enemy_group']['height']
            # Обновляем размеры дочерних компонентов групп
            # _update_panels будет использовать новые self.x, self.width
            self.enemy_group._update_panels()

        # Обновляем размеры и позиции лога боя
        if self.battle_log:
            self.battle_log.x = layout['battle_log']['x']
            self.battle_log.y = layout['battle_log']['y']
            self.battle_log.width = layout['battle_log']['width']
            self.battle_log.height = layout['battle_log']['height']
            # BattleLog не имеет сложной внутренней структуры панелей,
            # поэтому явный вызов update_size не требуется.
            # Если бы требовался, нужно было бы проверить сигнатуру метода в BattleLog.

        # --- КОНЕЦ ОБНОВЛЕННОЙ ЛОГИКИ ---

    def _setup_commands(self) -> None:
        """Настройка дополнительных команд экрана."""
        # Все команды добавятся автоматически из реестра!
        pass

    # - ОБНОВЛЯЕМ МЕТОД render -
    def render(self, stdscr: curses.window) -> None:
        """Отрисовка экрана."""
        # Обновляем размеры компонентов перед отрисовкой
        self._update_component_sizes()
        self.renderer.clear()

        # Отрисовка стандартного макета (шапка + подвал)
        self.render_standard_layout("=== БОЙ ===")

        # - ОТРИСОВКА НОВЫХ КОМПОНЕНТОВ -
        # Отрисовываем компоненты напрямую
        if self.player_group:
            self.player_group.render(self.renderer)
        if self.enemy_group:
            self.enemy_group.render(self.renderer)
        if self.battle_log:
            self.battle_log.render(self.renderer)
        # -
        self.renderer.refresh() # Не забываем refresh

    def _handle_unregistered_key(self, key: int) -> None:
        """Обработка незарегистрированных клавиш."""
        # Обработка прокрутки лога
        if key == curses.KEY_UP:
            if self.battle_log:
                self.battle_log.scroll_up()
        elif key == curses.KEY_DOWN:
            if self.battle_log:
                self.battle_log.scroll_down()
        # Можно добавить отладочный вывод
        # print(f"BattleScreen: Нажата незарегистрированная клавиша: {key}")
