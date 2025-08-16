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
# Импортируем get_game_manager для использования внутри _setup_elements
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
        # Они будут инициализированы в _setup_elements
        self.player_group: 'PlayerGroupPanel' = None # type: ignore
        self.enemy_group: 'EnemyGroupPanel' = None # type: ignore
        self.battle_log: 'BattleLog' = None # type: ignore

        # Вызываем родительский конструктор
        # _setup_elements будет вызван внутри него
        super().__init__(manager)

        # После вызова super().__init__ все атрибуты уже инициализированы
        # Дополнительная инициализация, если потребуется, может быть здесь

    def _setup_elements(self) -> None:
        """Настройка элементов экрана."""
        
        self.elements = [] # Очищаем список, так как компоненты будут отрисовываться напрямую

        # --- ПОЛУЧАЕМ ДАННЫЕ ИЗ GameManager НЕПОСРЕДСТВЕННО В _setup_elements ---
        # Это решает проблему порядка инициализации
        game_manager = get_game_manager()
        real_enemy_data = game_manager.get_current_enemies()
        real_player_data = game_manager.get_player_group()
        # ---

        # - НАСТРОЙКА КОМПОНЕНТОВ -
        # Инициализируем компоненты с начальными размерами
        # Они будут обновлены в render/update_size
        header_height = 2
        
        # Начальные координаты для блоков юнитов
        units_y = header_height + 1 # Блоки юнитов под заголовком
        units_height = 5 # Фиксированная высота 5 строк
        
        # Ширины блоков
        total_width = 80 # Начальное значение, будет пересчитано в update_size
        player_group_width = total_width // 3
        enemy_group_width = total_width - player_group_width - 1 # -1 для зазора
        
        # Координаты X
        player_group_x = 1
        enemy_group_x = player_group_x + player_group_width + 1 # +1 для зазора

        # Создаем панели с реальными объектами Character
        # EnemyGroupPanel и PlayerGroupPanel теперь принимают List[Monster] и List[Player]
        self.player_group = PlayerGroupPanel(
            x=player_group_x,
            y=units_y,
            width=player_group_width,
            height=units_height,
            players=real_player_data # Передаем список объектов Player напрямую
        )

        self.enemy_group = EnemyGroupPanel(
            x=enemy_group_x,
            y=units_y,
            width=enemy_group_width,
            height=units_height,
            enemies=real_enemy_data # Передаем список объектов Monster напрямую
        )

        # Временные координаты для battle_log, будут обновлены в update_size
        log_x = 1
        log_y = units_y + units_height + 1 # Под блоками юнитов
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

        # Получаем текущие размеры экрана
        screen_width = self.renderer.width
        screen_height = self.renderer.height
        
        # Координаты и размеры
        header_height = 2
        
        # Блоки юнитов
        units_y = header_height + 1
        units_height = 5 # Фиксированная высота
        
        # Ширины блоков (1/3 для игроков, 2/3 для монстров)
        player_group_width = max(10, screen_width // 3)
        enemy_group_width = max(10, screen_width - player_group_width - 1) # -1 для зазора
        
        # Координаты X
        player_group_x = 1
        enemy_group_x = player_group_x + player_group_width + 1 # +1 для зазора

        # Обновляем размеры и позиции групп
        self.player_group.x = player_group_x
        self.player_group.y = units_y
        self.player_group.width = player_group_width
        self.player_group.height = units_height

        self.enemy_group.x = enemy_group_x
        self.enemy_group.y = units_y
        self.enemy_group.width = enemy_group_width
        self.enemy_group.height = units_height

        # Обновляем размеры дочерних компонентов групп
        # Для GroupPanel update_size принимает общие размеры экрана
        self.player_group.update_size(screen_width, screen_height)
        self.enemy_group.update_size(screen_width, screen_height)

        # Лог боя
        log_x = 1
        log_y = units_y + units_height + 1 # Под блоками юнитов
        log_width = max(10, screen_width - 2) # На всю ширину с отступами
        
        # Высота лога - всё оставшееся пространство минус отступы и подвал
        available_height = screen_height - log_y - 2 # -2 для подвала
        log_height = max(3, available_height) # Минимальная высота 3

        self.battle_log.x = log_x
        self.battle_log.y = log_y
        self.battle_log.width = log_width
        self.battle_log.height = log_height
        # Исправленный вызов update_size для BattleLog
        # Сигнатура: update_size(self, total_width: int, total_height: int)
        self.battle_log.update_size(screen_width, screen_height)

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
