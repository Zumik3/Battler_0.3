# game/ui/battle_screen.py
"""
Экран боя.
Отображает боевую сцену с возможностью взаимодействия.
"""
import curses
from typing import TYPE_CHECKING

# --- ДОБАВЛЯЕМ ИМПОРТ МИКСИНА ---
from game.ui.mixins import StandardLayoutMixin
# --------------------------------
# --- ИМПОРТИРУЕМ НОВЫЕ КОМПОНЕНТЫ ---
from game.ui.components.battle_components import (
    PlayerUnitPanel, 
    EnemyUnitPanel, 
    GroupPanel, 
    BattleLog
)
# ------------------------------------
from game.ui.base_screen import BaseScreen
from game.ui.rendering.color_manager import Color

# --- ДОБАВЛЯЕМ ИМПОРТ ДЛЯ TYPE_CHECKING ---
if TYPE_CHECKING:
    from game.ui.screen_manager import ScreenManager
# ------------------------------------------

# --- НАСЛЕДУЕМСЯ ОТ StandardLayoutMixin ---
class BattleScreen(BaseScreen, StandardLayoutMixin):
    """Экран боя."""

    def __init__(self, manager: 'ScreenManager'):
        # Инициализируем атрибуты для компонентов
        self.player_group: GroupPanel = None # type: ignore # Будет инициализирован в _setup_elements
        self.enemy_group: GroupPanel = None # type: ignore
        self.battle_log: BattleLog = None # type: ignore
        super().__init__(manager)

    def _setup_elements(self) -> None:
        """Настройка элементов экрана."""
        # УБИРАЕМ старый заголовок и разделитель, так как они теперь в миксине
        self.elements = [] # Очищаем список, так как компоненты будут отрисовываться напрямую
        
        # --- НАСТРОЙКА КОМПОНЕНТОВ ---
        # Инициализируем компоненты с начальными размерами
        # Они будут обновлены в render/update_size
        header_height = 2
        initial_group_height = 6 # Примерная высота для группы (может быть динамической)
        player_group_x = 1
        player_group_y = header_height
        # enemy_group_x будет рассчитан в update_size
        enemy_group_y = header_height
        log_x = 1
        # log_y будет рассчитан в update_size
        log_width = max(10, self.renderer.width - 2)
        # log_height будет рассчитан в update_size
        
        # Создаем группы и лог с начальными параметрами
        self.player_group = GroupPanel(
            player_group_x, player_group_y, 
            self.renderer.width // 2 - 1, initial_group_height, 
            "Игроки"
        )
        # Временные координаты для enemy_group, будут обновлены в update_size
        self.enemy_group = GroupPanel(
            self.renderer.width // 2 + 1, enemy_group_y, 
            self.renderer.width // 2 - 1, initial_group_height, 
            "Враги"
        )
        
        # Добавляем тестовые панели юнитов
        # В реальной игре это будет делаться на основе данных о бое
        player1 = PlayerUnitPanel(0, 0, 30, "Герой", 100, 100, 50, 50)
        player2 = PlayerUnitPanel(0, 0, 30, "Соратник", 80, 80, 30, 30)
        self.player_group.add_unit_panel(player1)
        self.player_group.add_unit_panel(player2)
        
        enemy1 = EnemyUnitPanel(0, 0, 30, "Дракон", 150, 150)
        enemy2 = EnemyUnitPanel(0, 0, 30, "Гоблин", 40, 40)
        self.enemy_group.add_unit_panel(enemy1)
        self.enemy_group.add_unit_panel(enemy2)
        
        # Временные координаты для battle_log, будут обновлены в update_size
        self.battle_log = BattleLog(log_x, header_height + initial_group_height + 1, log_width, 10)
        
        # Обновляем размеры компонентов
        self._update_component_sizes()

    def _update_component_sizes(self) -> None:
        """Обновление размеров всех компонентов."""
        if not (self.player_group and self.enemy_group and self.battle_log):
            return
            
        # Обновляем размеры групп
        group_width = max(10, self.renderer.width // 2 - 1)
        # Высота групп может быть фиксированной или рассчитанной, пока фиксированная
        group_height = max(3, min(10, len(self.player_group.unit_panels) + 2, len(self.enemy_group.unit_panels) + 2))
        
        self.player_group.width = group_width
        self.player_group.height = group_height
        self.enemy_group.x = max(0, self.renderer.width // 2 + 1)
        self.enemy_group.width = group_width
        self.enemy_group.height = group_height
        
        # Обновляем размеры и позицию лога
        log_y = self.player_group.y + group_height + 1
        self.battle_log.x = 1
        self.battle_log.y = log_y
        self.battle_log.width = max(10, self.renderer.width - 2)
        # Лог занимает всё оставшееся пространство до подвала (2 строки)
        footer_height = 2
        self.battle_log.height = max(3, self.renderer.height - log_y - footer_height)
        
        # Обновляем размеры дочерних компонентов, если у них есть такой метод
        # (в данном случае GroupPanel сам управляет своими UnitPanel)
        # BattleLog и GroupPanel имеют свои методы update_size, но они простые
        # Для BattleLog update_size в текущей реализации пустой, но можно расширить
        # self.battle_log.update_size(self.renderer.width, self.renderer.height)
        # self.player_group.update_size(self.renderer.width, self.renderer.height)
        # self.enemy_group.update_size(self.renderer.width, self.renderer.height)

    def _setup_commands(self) -> None:
        """Настройка дополнительных команд экрана."""
        # Все команды добавятся автоматически из реестра!
        pass

    # --- ОБНОВЛЯЕМ МЕТОД render ---
    def render(self, stdscr: curses.window) -> None:
        """Отрисовка экрана."""
        # Обновляем размеры компонентов перед отрисовкой
        self._update_component_sizes()
        
        self.renderer.clear()
        # Отрисовка стандартного макета (шапка + подвал)
        self.render_standard_layout("=== БОЙ ===")
        
        # --- ОТРИСОВКА НОВЫХ КОМПОНЕНТОВ ---
        # Отрисовываем компоненты напрямую
        if self.player_group:
            self.player_group.render(self.renderer)
        if self.enemy_group:
            self.enemy_group.render(self.renderer)
        if self.battle_log:
            self.battle_log.render(self.renderer)
        # ------------------------------------
        
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
