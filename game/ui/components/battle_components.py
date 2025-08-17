# game/ui/components/battle_components.py
"""Компоненты для экрана боя.
Содержит визуальные элементы для отображения игроков, врагов и лога боя."""

import curses
from typing import List, TYPE_CHECKING

from game.ui.rendering.renderable import Renderable
from game.ui.rendering.renderer import Renderer
from game.ui.rendering.color_manager import Color
# Импортируем новые виджеты
from game.ui.widgets.labels import CharacterNameLabel, CharacterLevelLabel, CharacterClassLabel, TextLabel
from game.ui.widgets.bars import HealthBar, EnergyBar

# Импорты для аннотаций типов, чтобы избежать циклических импортов на уровне выполнения
if TYPE_CHECKING:
    from game.entities.monster import Monster
    from game.entities.player import Player
    from game.entities.character import Character


class UnitPanel(Renderable):
    """Базовая панель для отображения одного юнита (игрока или врага) в одну строку."""
    
    # Константы для компоновки
    DEFAULT_WIDGET_MAX_WIDTH = 10
    MIN_NAME_WIDTH = 5
    MIN_WIDGET_WIDTH = 3
    WIDGET_SPACING = 1
    CHARACTER_NAME_WIDTH = 6  # Все имена персонажей состоят из максимум 6 букв. 
    MONSTER_NAME_WIDTH = 20
    HP_BAR_WIDTH = 10
    EP_BAR_WIDTH = 5
    
    # Константы для оценки минимальной ширины элементов
    ESTIMATED_LEVEL_WIDTH = 3
    ESTIMATED_HP_WIDTH = 10  # Обновлено для прогресс-баров
    ESTIMATED_ENERGY_WIDTH = 5  # Обновлено для прогресс-баров
    
    # Пороги для цветов HP
    HP_CRITICAL_THRESHOLD = 0.25
    HP_LOW_THRESHOLD = 0.5

    def __init__(self, character: 'Character', x: int, y: int, width: int, height: int) -> None:
        """Инициализация базовой панели юнита.
        Args:
            x: Координата X.
            y: Координата Y.
            width: Ширина панели.
            height: Высота панели (должна быть 1 для соответствия новому дизайну).
        """
        super().__init__(x, y)
        self.width = width
        self.height = height  # Ожидается 1
        self.character = character
        
        if character.is_player:
            name_width = self.CHARACTER_NAME_WIDTH 
            color = Color.GREEN
        else:
            name_width = self.MONSTER_NAME_WIDTH
            color = Color.BLUE

        # Инициализируем виджеты
        self.name_label = CharacterNameLabel(character=self.character, x=x, y=y, max_width=name_width, color=color)
        self.class_label = CharacterClassLabel(character=self.character, x=x, y=y)
        self.level_label = CharacterLevelLabel(character=self.character, x=x, y=y)
        
        self.hp_label = HealthBar(character=self.character, x=x, y=y, width=self.HP_BAR_WIDTH)
        self.energy_label = EnergyBar(character=character, x=x, y=y, width=self.EP_BAR_WIDTH)
        # Для HP и Energy в бою отображаем числовые значения, а не прогресс-бары
        # Поэтому создаем специальные текстовые лейблы
        #self.hp_label = TextLabel(x=x, y=y)
        #self.energy_label = TextLabel(x=x, y=y)

    def update_size(self, width: int, height: int) -> None:
        """
        Обновить размеры панели и пересчитать позиции виджетов.
        
        Args:
            width: Новая ширина.
            height: Новая высота (игнорируется, устанавливается в 1).
        """
        self.width = width
        self.height = 1  # Фиксированная высота для однострочной панели
        
        # Пересчитываем позиции виджетов
        self._update_widgets_positions()

    def _update_widgets_positions(self) -> None:
        """Обновить позиции и размеры виджетов в зависимости от ширины панели."""
        if not self.character:
            return
            
        current_x = self.x
        
        # 1. Имя
        self.name_label.x = current_x
        self.name_label.y = self.y
        name_width = self.name_label.max_width
        current_x += name_width + self.WIDGET_SPACING

        # 2. Класс/роль
        self.class_label.x = current_x
        self.class_label.y = self.y
        class_width = len(self.class_label.text) + 2  # Примерная ширина [R]
        current_x += class_width  #  Spacing не нужен 
        
        # 3. Уровень
        self.level_label.x = current_x
        self.level_label.y = self.y
        level_width = len(self.level_label.text) + 2
        current_x += level_width

        # 4. HP
        self.hp_label.x = current_x
        self.hp_label.y = self.y
        current_x += self.hp_label.width + 2
        
        # 5. Energy
        self.energy_label.x = current_x
        self.energy_label.y = self.y

    def render(self, renderer: Renderer) -> None:
        """Отрисовка базовой панели юнита в одну строку."""
        if not self.character:
            # Если персонаж не установлен, отображаем заглушку
            placeholder_text = "Нет данных"
            display_text = placeholder_text.ljust(self.width)[:self.width]
            try:
                renderer.draw_text(display_text, self.x, self.y, color=Color.GRAY)
            except curses.error:
                pass
            return

        # Пересчитываем позиции виджетов перед отрисовкой
        self._update_widgets_positions()
        
        # Отрисовываем все виджеты
        self.name_label.render(renderer)
        self.class_label.render(renderer)
        self.level_label.render(renderer)
        self.hp_label.render(renderer)
        self.energy_label.render(renderer)
            
        # Заполняем оставшееся пространство пробелами для затирания предыдущего содержимого
        # last_widget_end_x = self.energy_label.x + len(self.energy_label.text) if self.energy_label.text else \
        #                   (self.hp_label.x + len(self.hp_label.text))
        # if last_widget_end_x < self.x + self.width:
        #     remaining_width = (self.x + self.width) - last_widget_end_x
        #     try:
        #         renderer.draw_text(" " * remaining_width, last_widget_end_x, self.y)
        #     except curses.error:
        #         pass


class EnemyUnitPanel(UnitPanel):
    """Панель для отображения одного врага."""

    def __init__(self, x: int, y: int, width: int, height: int, monster: 'Monster') -> None:
        """Инициализация панели врага.
        Args:
            x: Координата X.
            y: Координата Y.
            width: Ширина панели.
            height: Высота панели (должна быть 1).
            monster: Объект Monster для отображения.
        """
        super().__init__(monster, x, y, width, height)


class PlayerUnitPanel(UnitPanel):
    """Панель для отображения одного игрока."""

    def __init__(self, x: int, y: int, width: int, height: int, player: 'Player') -> None:
        """Инициализация панели игрока.
        Args:
            x: Координата X.
            y: Координата Y.
            width: Ширина панели.
            height: Высота панели (должна быть 1).
            player: Объект Player для отображения.
        """
        super().__init__(player, x, y, width, height)


class GroupPanel(Renderable):
    """Базовая панель для отображения группы юнитов без внешнего обрамления."""

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """Инициализация базовой панели группы.
        Args:
            x: Координата X.
            y: Координата Y.
            width: Ширина панели.
            height: Высота панели.
        """
        super().__init__(x, y)
        self.width = width
        self.height = height
        # Этот список будет заполняться в подклассах
        self.panels: List[UnitPanel] = []

    def update_size(self, max_width: int, max_height: int) -> None:
        """
        Обновление размеров панели и её компонентов.
        Args:
            max_width: Максимальная ширина экрана.
            max_height: Максимальная высота экрана.
        """
        # Обновление размеров дочерних панелей
        if self.panels:
            # Рассчитываем ширину для каждой панели
            panel_count = len(self.panels)
            new_panel_width = max(10, self.width // panel_count) if panel_count > 0 else self.width

            for i, panel in enumerate(self.panels):
                panel.width = new_panel_width
                panel.height = 1  # Высота панели юнита должна быть 1
                panel.update_size(new_panel_width, 1)  # Обновляем размеры внутренних виджетов

    def render(self, renderer: Renderer) -> None:
        """Отрисовка панели группы без внешнего обрамления."""
        # НЕ отрисовываем рамку вокруг группы
        # Отрисовка каждой панели юнита
        for panel in self.panels:
            panel.render(renderer)


class EnemyGroupPanel(GroupPanel):
    """Панель для отображения группы врагов."""

    def __init__(self, x: int, y: int, width: int, height: int, enemies: List['Monster']) -> None:
        """Инициализация панели группы врагов.
        Args:
            x: Координата X.
            y: Координата Y.
            width: Ширина панели.
            height: Высота панели (ожидается 5).
            enemies: Список объектов Monster для отображения.
        """
        # Инициализируем базовую панель группы
        super().__init__(x, y, width, height)
        # Сохраняем ссылку на список объектов Monster
        self.enemies = enemies
        # Обновляем панели на основе переданных объектов
        self._update_panels()

    def _update_panels(self) -> None:
        """Обновление списка панелей на основе объектов врагов."""
        self.panels = []
        
        for i, monster in enumerate(self.enemies):
            # Каждая панель размещается на отдельной строке
            panel_x = self.x
            panel_y = self.y + i  # Одна строка на панель
            panel_width = self.width
            panel_height = 1  # Фиксированная высота 1 строка
            
            # Создаем панель, передавая объект Monster
            panel = EnemyUnitPanel(panel_x, panel_y, panel_width, panel_height, monster)
            self.panels.append(panel)


class PlayerGroupPanel(GroupPanel):
    """Панель для отображения группы игроков."""

    def __init__(self, x: int, y: int, width: int, height: int, players: List['Player']) -> None:
        """Инициализация панели группы игроков.
        Args:
            x: Координата X.
            y: Координата Y.
            width: Ширина панели.
            height: Высота панели (ожидается 5).
            players: Список объектов Player для отображения.
        """
        # Инициализируем базовую панель группы
        super().__init__(x, y, width, height)
        # Сохраняем ссылку на список объектов Player
        self.players = players
        # Обновляем панели на основе переданных объектов
        self._update_panels()

    def _update_panels(self) -> None:
        """Обновление списка панелей на основе объектов игроков."""
        self.panels = []
        
        for i, player in enumerate(self.players):
            # Каждая панель размещается на отдельной строке
            panel_x = self.x
            panel_y = self.y + i  # Одна строка на панель
            panel_width = self.width
            panel_height = 1  # Фиксированная высота 1 строка
            
            # Создаем панель, передавая объект Player
            panel = PlayerUnitPanel(panel_x, panel_y, panel_width, panel_height, player)
            self.panels.append(panel)


class BattleLog(Renderable):
    """Лог боя в нижней части экрана с прокруткой и обрамлением."""

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        super().__init__(x, y)
        self.width = width
        self.height = height
        # TODO: Получать реальные сообщения из игровой логики
        self.messages: List[str] = [
            "Битва начинается!",
            "Герой вступает в бой с Драконом.",
            "Дракон издает грозный рык.",
            "Герой атакует Дракона!",
            "Дракон получает 25 урона.",
            "Дракон атакует Героя!",
            "Герой получает 15 урона.",
            "Герой использует зелье лечения.",
            "Герой восстанавливает 30 HP.",
            "Дракон готовится к мощной атаке!",
            "Герой защищается.",
            "Мощная атака Дракона отражена!",
        ]
        self.scroll_offset = 0 # Смещение прокрутки (0 = последние сообщения внизу)

    def add_message(self, message: str) -> None:
        """Добавление сообщения в лог.
        Args:
            message: Текст сообщения.
        """
        self.messages.append(message)
        # При добавлении нового сообщения сбрасываем прокрутку вниз
        self.scroll_offset = 0

    def scroll_up(self) -> None:
        """Прокрутка лога вверх."""
        # Максимальное смещение - это количество строк, которые не помещаются
        max_offset = max(0, len(self.messages) - self.height)
        if self.messages:
            self.scroll_offset = min(max_offset, self.scroll_offset + 1)

    def scroll_down(self) -> None:
        """Прокрутка лога вниз."""
        if self.messages:
            self.scroll_offset = max(0, self.scroll_offset - 1)

    def update_size(self, total_width: int, total_height: int) -> None:
        """Обновление размеров лога.
        Args:
            total_width: Общая ширина экрана.
            total_height: Общая высота экрана.
        """
        # Занимает всю ширину экрана (с отступами)
        self.width = max(10, total_width - 2) # -2 для отступов
        # Высота динамическая, устанавливается в BattleScreen._update_component_sizes
        # Пока оставим пустую реализацию или базовую
        pass

    def render(self, renderer: Renderer) -> None:
        """Отрисовка лога боя с обрамлением."""
        # Отрисовка рамки лога (она остается)
        try:
            renderer.draw_borderless_log_box(self.x, self.y, self.width, self.height)
        except curses.error:
            # Игнорируем ошибки выхода за границы экрана
            pass

        # Определяем, какие сообщения отображать с учетом прокрутки
        # scroll_offset = 0 означает, что последние сообщения внизу
        start_index = max(0, len(self.messages) - self.height - self.scroll_offset)
        end_index = start_index + self.height
        visible_messages = self.messages[start_index:end_index]

        # Отрисовка сообщений
        for i, message in enumerate(visible_messages):
            # Позиция Y для текущего сообщения
            msg_y = self.y + 1 + i
            # Позиция X (с небольшим отступом)
            msg_x = self.x + 1

            # Отрисовка текста сообщения
            try:
                # TODO: Добавить цвета/стили для разных типов сообщений (урон, лечение, и т.д.)
                renderer.draw_text(message, msg_x, msg_y, color=Color.WHITE)
            except curses.error:
                # Игнорируем ошибки выхода за границы экрана
                pass
