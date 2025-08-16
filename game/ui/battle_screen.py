# game/ui/battle_screen.py
"""Экран боя.
Отображает боевую сцену с возможностью взаимодействия."""

import curses
from typing import TYPE_CHECKING

# - ДОБАВЛЯЕМ ИМПОРТ МИКСИНА -
from game.ui.mixins import StandardLayoutMixin
# -

# - ИМПОРТИРУЕМ НОВЫЕ КОМПОНЕНТЫ -
from game.ui.components.battle_components import (
    PlayerUnitPanel,
    EnemyUnitPanel,
    GroupPanel,
    BattleLog
)
# -
from game.ui.base_screen import BaseScreen
from game.ui.rendering.color_manager import Color

# - ДОБАВЛЯЕМ ИМПОРТ ДЛЯ TYPE_CHECKING -
if TYPE_CHECKING:
    from game.ui.screen_manager import ScreenManager
    from game.entities.player import Player # Для аннотаций
# -


# - НАСЛЕДУЕМСЯ ОТ StandardLayoutMixin -
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

        # - НАСТРОЙКА КОМПОНЕНТОВ -
        # Инициализируем компоненты с начальными размерами
        # Они будут обновлены в render/update_size
        header_height = 2
        initial_group_height = 6 # Примерная высота для группы (может быть динамической)
        player_group_x = 1
        player_group_y = header_height
        enemy_group_x = 1
        enemy_group_y = player_group_y + initial_group_height + 1 # +1 для разделителя

        self.player_group = GroupPanel(player_group_x, player_group_y, 50, initial_group_height, "Герои")
        self.enemy_group = GroupPanel(enemy_group_x, enemy_group_y, 50, initial_group_height, "Враги")

        # --- СТАРОЕ: Создание тестовых панелей ---
        # # Добавляем тестовые панели юнитов
        # # В реальной игре это будет делаться на основе данных о бое
        # player1 = PlayerUnitPanel(0, 0, 30, "Герой", 100, 100, 50, 50)
        # player2 = PlayerUnitPanel(0, 0, 30, "Соратник", 80, 80, 30, 30)
        # self.player_group.add_unit_panel(player1)
        # self.player_group.add_unit_panel(player2)
        # enemy1 = EnemyUnitPanel(0, 0, 30, "Дракон", 150, 150)
        # enemy2 = EnemyUnitPanel(0, 0, 30, "Гоблин", 40, 40)
        # self.enemy_group.add_unit_panel(enemy1)
        # self.enemy_group.add_unit_panel(enemy2)
        # --- КОНЕЦ СТАРОГО кода ---

        # --- НОВОЕ: Создание панелей на основе данных из GameManager ---
        # Получаем группу игроков из GameManager
        if self.manager and hasattr(self.manager, 'game_manager'):
            player_characters = self.manager.game_manager.get_player_group()

            # Создаем панели для каждого игрока
            for i, player_char in enumerate(player_characters):
                # Создаем PlayerUnitPanel, используя данные реального персонажа
                # Предполагаем, что player_char имеет атрибуты name, hp, energy, attributes
                player_panel = PlayerUnitPanel(
                    x=0,  # Координаты будут обновлены в _update_component_sizes
                    y=0,  # Координаты будут обновлены в _update_component_sizes
                    width=30, # Ширина может быть скорректирована позже
                    name=player_char.name,
                    hp=player_char.hp,
                    max_hp=player_char.attributes.max_hp,
                    mp=player_char.energy, # Предполагаем, что энергия отображается как MP
                    max_mp=player_char.attributes.max_energy # Предполагаем, что макс. энергия отображается как макс. MP
                )
                # Добавляем панель в группу
                self.player_group.add_unit_panel(player_panel)

        # (Пока) оставляем создание врагов как в оригинале, или можно также обновить
        # если будет фабрика монстров в GameManager
        enemy1 = EnemyUnitPanel(0, 0, 30, "Дракон", 150, 150)
        enemy2 = EnemyUnitPanel(0, 0, 30, "Гоблин", 40, 40)
        self.enemy_group.add_unit_panel(enemy1)
        self.enemy_group.add_unit_panel(enemy2)
        # --- КОНЕЦ НОВОГО кода ---

        # Временные координаты для battle_log, будут обновлены в update_size
        log_x = 1
        log_y = enemy_group_y + initial_group_height + 1
        log_width = 60
        log_height = 5
        self.battle_log = BattleLog(log_x, log_y, log_width, log_height)

        # Добавляем тестовые сообщения в лог
        # TODO: Заменить на реальные сообщения из игровой логики
        self.battle_log.add_message("Битва начинается!")
        # self.battle_log.add_message("Герой вступает в бой с Драконом.")
        # self.battle_log.add_message("Дракон издает грозный рык.")
        # self.battle_log.add_message("Герой атакует Дракона!")
        # self.battle_log.add_message("Дракон получает 25 урона.")
        # self.battle_log.add_message("Дракон атакует Героя!")
        # self.battle_log.add_message("Герой получает 15 урона.")
        # self.battle_log.add_message("Герой использует зелье лечения.")
        # self.battle_log.add_message("Герой восстанавливает 30 HP.")
        # self.battle_log.add_message("Дракон готовится к мощной атаке!")
        # self.battle_log.add_message("Герой защищается.")
        # self.battle_log.add_message("Мощная атака Дракона отражена!")

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
