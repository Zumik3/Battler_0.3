# game/ui/screens/battle_screen.py
"""Экран боя.
Отображает боевую сцену с возможностью взаимодействия."""

import curses
from typing import TYPE_CHECKING

# - ДОБАВЛЯЕМ ИМПОРТ МИКСИНА -
from game.ui.mixins import StandardLayoutMixin
# -

# - ИМПОРТИРУЕМ НОВЫЕ КОМПОНЕНТЫ -
from game.ui.components.battle_components import (
    PlayerGroupPanel,
    EnemyGroupPanel,
    BattleLog
)
# -
from game.ui.base_screen import BaseScreen
from game.ui.rendering.color_manager import Color
from game.game_manager import get_game_manager

# - ДОБАВЛЯЕМ ИМПОРТ ДЛЯ TYPE_CHECKING -
if TYPE_CHECKING:
    from game.ui.screen_manager import ScreenManager
    from game.entities.player import Player # Для аннотаций
    from game.entities.monster import Monster # Для аннотаций
# -


# - НАСЛЕДУЕМСЯ ОТ StandardLayoutMixin -
class BattleScreen(BaseScreen, StandardLayoutMixin):
    """Экран боя."""

    def __init__(self, manager: 'ScreenManager'):
        # Инициализируем атрибуты для компонентов
        # Используем аннотации типов, так как присваивание будет позже
        self.player_group: 'PlayerGroupPanel'
        self.enemy_group: 'EnemyGroupPanel'
        self.battle_log: 'BattleLog'

        super().__init__(manager)

    def _setup_elements(self) -> None:
        """Настройка элементов экрана."""
        
        self.elements = [] # Очищаем список, так как компоненты будут отрисовываться напрямую

        # - НАСТРОЙКА КОМПОНЕНТОВ -
        # Инициализируем компоненты с начальными размерами
        # Они будут обновлены в render/update_size
        header_height = 2
        initial_group_height = 6 # Примерная высота для группы (может быть динамической)
        player_group_x = 1
        player_group_y = header_height
        enemy_group_x = 1
        enemy_group_y = player_group_y + initial_group_height + 1 # +1 для разделителя

         # Получаем экземпляр GameManager
        self.game_manager = get_game_manager()

        # Получаем реальные данные из GameManager
        self.real_enemy_data = self.game_manager.get_current_enemies()
        self.real_player_data = self.game_manager.get_player_group()

        # Создаем панели с реальными объектами Character
        # EnemyGroupPanel и PlayerGroupPanel теперь принимают List[Monster] и List[Player]
        self.enemy_group = EnemyGroupPanel(
            x=enemy_group_x,
            y=enemy_group_y,
            width=50,  # Ширина будет обновлена в _update_component_sizes
            height=initial_group_height,
            enemies=self.real_enemy_data # Передаем список объектов Monster напрямую
        )

        self.player_group = PlayerGroupPanel(
            x=player_group_x,
            y=player_group_y,
            width=50,  # Ширина будет обновлена в _update_component_sizes
            height=initial_group_height,
            players=self.real_player_data # Передаем список объектов Player напрямую
        )

        # Временные координаты для battle_log, будут обновлены в update_size
        log_x = 1
        log_y = enemy_group_y + initial_group_height + 1
        log_width = 60
        log_height = 5
        self.battle_log = BattleLog(log_x, log_y, log_width, log_height)

        # Добавляем тестовые сообщения в лог
        # TODO: Заменить на реальные сообщения из игровой логики
        self.battle_log.add_message("Битва начинается!")

    def _update_component_sizes(self) -> None:
        """Обновление размеров компонентов."""
        if not self.renderer:
            return

        # Координаты и размеры
        header_height = 2
        group_width = max(10, self.renderer.width - 2)
        group_height = 6 # Примерная высота, можно сделать динамической

        # Группы игроков и врагов
        self.player_group.x = 1
        self.player_group.y = header_height
        self.player_group.width = group_width
        self.player_group.height = group_height

        self.enemy_group.x = 1
        self.enemy_group.y = header_height + group_height + 1
        self.enemy_group.width = group_width
        self.enemy_group.height = group_height

        # Обновляем размеры дочерних компонентов
        self.player_group.update_size(self.renderer.width, self.renderer.height)
        self.enemy_group.update_size(self.renderer.width, self.renderer.height)

        # Лог боя
        log_x = 1
        log_y = header_height + 2 * group_height + 2
        log_width = max(10, self.renderer.width - 2)
        # Высота лога - всё оставшееся пространство минус отступы
        available_height = self.renderer.height - log_y - 2 # -2 для подвала
        log_height = max(3, available_height) # Минимальная высота 3

        self.battle_log.x = log_x
        self.battle_log.y = log_y
        self.battle_log.width = log_width
        self.battle_log.height = log_height
        self.battle_log.update_size(self.renderer.width, self.renderer.height)

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
