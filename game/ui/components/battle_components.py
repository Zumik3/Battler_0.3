# game/ui/components/battle_components.py
"""Компоненты для экрана боя.
Содержит визуальные элементы для отображения игроков, врагов и лога боя."""

import curses
from typing import List, Dict, Any, TYPE_CHECKING

from game.ui.rendering.renderable import Renderable
from game.ui.rendering.color_manager import Color
from game.ui.rendering.renderer import Renderer

# Импорты для аннотаций типов, чтобы избежать циклических импортов на уровне выполнения
if TYPE_CHECKING:
    from game.entities.monster import Monster
    from game.entities.player import Player
    from game.entities.character import Character


class UnitPanel(Renderable):
    """Базовая панель для отображения одного юнита (игрока или врага)."""

    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        """Инициализация базовой панели юнита.
        Args:
            x: Координата X.
            y: Координата Y.
            width: Ширина панели.
            height: Высота панели.
        """
        super().__init__(x, y)
        self.width = width
        self.height = height
        # Эти атрибуты будут устанавливаться в подклассах или методах обновления
        self.name: str = "Unknown"
        self.max_hp: int = 1
        self.current_hp: int = 1
        self.max_mp: int = 0
        self.current_mp: int = 0
        self.is_player: bool = False

    def render(self, renderer: Renderer) -> None:
        """Отрисовка базовой панели юнита."""
        # Отрисовка рамки
        renderer.draw_box(self.x, self.y, self.width, self.height)

        # Определение цвета в зависимости от типа юнита
        color = Color.CYAN if self.is_player else Color.RED

        # Отрисовка содержимого (имя, HP/MP)
        hp_text = f"HP: {self.current_hp}/{self.max_hp}"
        mp_text = f"MP: {self.current_mp}/{self.max_mp}" if self.max_mp > 0 else ""

        # Позиции для текста внутри рамки
        name_x = self.x + 1
        name_y = self.y + 1
        hp_x = self.x + 1
        hp_y = self.y + 2
        mp_x = self.x + 1
        mp_y = self.y + 3

        # Отрисовка имени
        try:
            renderer.draw_text(self.name, name_x, name_y, color=color, bold=True)
        except curses.error:
            # Игнорируем ошибки выхода за границы экрана
            pass

        # Отрисовка HP
        try:
            renderer.draw_text(hp_text, hp_x, hp_y, color=color)
        except curses.error:
            pass

        # Отрисовка MP, если применимо
        if mp_text:
            try:
                renderer.draw_text(mp_text, mp_x, mp_y, color=color)
            except curses.error:
                pass


class EnemyUnitPanel(UnitPanel):
    """Панель для отображения одного врага."""

    def __init__(self, x: int, y: int, width: int, height: int, monster: 'Monster') -> None:
        """Инициализация панели врага.
        Args:
            x: Координата X.
            y: Координата Y.
            width: Ширина панели.
            height: Высота панели.
            monster: Объект Monster для отображения.
        """
        # Инициализируем базовую панель с минимальными значениями
        super().__init__(x, y, width, height)
        # Сохраняем ссылку на объект Monster
        self.monster = monster
        # Инициализируем данные из объекта Monster
        self._update_data_from_monster()

    def _update_data_from_monster(self) -> None:
        """Обновить внутренние данные панели из объекта Monster."""
        # Получаем актуальные данные из объекта Monster
        self.name = getattr(self.monster, 'name', 'Unknown Enemy')
        
        # HP
        self.current_hp = getattr(self.monster, 'hp', 0)
        # Получаем max_hp из атрибутов, если они есть
        attributes = getattr(self.monster, 'attributes', None)
        if attributes:
            self.max_hp = getattr(attributes, 'max_hp', 1)
        else:
            # Если атрибутов нет, используем текущий HP как максимум (или другое значение по умолчанию)
            self.max_hp = self.current_hp if self.current_hp > 0 else 1

        # MP
        self.current_mp = getattr(self.monster, 'mp', 0)
        if attributes:
            self.max_mp = getattr(attributes, 'max_mp', 0)
        else:
            self.max_mp = self.current_mp

        # is_player всегда False для EnemyUnitPanel
        self.is_player = False

    def render(self, renderer: Renderer) -> None:
        """Отрисовка панели врага."""
        # Перед отрисовкой обновляем данные из объекта Monster
        self._update_data_from_monster()
        # Вызываем родительский метод render, который использует обновленные self.name, self.current_hp и т.д.
        super().render(renderer)


class PlayerUnitPanel(UnitPanel):
    """Панель для отображения одного игрока."""

    def __init__(self, x: int, y: int, width: int, height: int, player: 'Player') -> None:
        """Инициализация панели игрока.
        Args:
            x: Координата X.
            y: Координата Y.
            width: Ширина панели.
            height: Высота панели.
            player: Объект Player для отображения.
        """
        # Инициализируем базовую панель с минимальными значениями
        super().__init__(x, y, width, height)
        # Сохраняем ссылку на объект Player
        self.player = player
        # Инициализируем данные из объекта Player
        self._update_data_from_player()

    def _update_data_from_player(self) -> None:
        """Обновить внутренние данные панели из объекта Player."""
        # Получаем актуальные данные из объекта Player
        self.name = getattr(self.player, 'name', 'Unknown Player')
        
        # HP
        self.current_hp = getattr(self.player, 'hp', 0)
        # Получаем max_hp из атрибутов, если они есть
        attributes = getattr(self.player, 'attributes', None)
        if attributes:
            self.max_hp = getattr(attributes, 'max_hp', 1)
        else:
            # Если атрибутов нет, используем текущий HP как максимум
            self.max_hp = self.current_hp if self.current_hp > 0 else 1

        # MP
        self.current_mp = getattr(self.player, 'mp', 0)
        if attributes:
            self.max_mp = getattr(attributes, 'max_mp', 0)
        else:
            self.max_mp = self.current_mp

        # is_player всегда True для PlayerUnitPanel
        self.is_player = True

    def render(self, renderer: Renderer) -> None:
        """Отрисовка панели игрока."""
        # Перед отрисовкой обновляем данные из объекта Player
        self._update_data_from_player()
        # Вызываем родительский метод render
        super().render(renderer)


class GroupPanel(Renderable):
    """Базовая панель для отображения группы юнитов."""

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
        """Обновление размеров панели и её компонентов.
        Args:
            max_width: Максимальная ширина экрана.
            max_height: Максимальная высота экрана.
        """
        # Простое обновление размеров самой панели
        self.width = max(10, max_width - 2) # Пример: занимает почти всю ширину
        # Высота может быть фиксированной или рассчитываться динамически
        # self.height = ... 

        # Обновление размеров дочерних панелей (если нужно)
        # Пока оставим базовую реализацию пустой, конкретная логика будет в подклассах
        # Например, можно пересчитать ширину каждой UnitPanel в группе
        if self.panels:
            panel_count = len(self.panels)
            new_panel_width = max(15, self.width // panel_count) if panel_count > 0 else 15
            for i, panel in enumerate(self.panels):
                panel.width = new_panel_width - 1 # -1 для отступа
                # Также можно обновить позицию X, если ширина изменилась
                panel.x = self.x + i * new_panel_width

    def render(self, renderer: Renderer) -> None:
        """Отрисовка панели группы."""
        # Отрисовка рамки группы
        renderer.draw_box(self.x, self.y, self.width, self.height)
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
            height: Высота панели.
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
        # Рассчитываем ширину для каждой панели
        panel_count = len(self.enemies) if self.enemies else 1 # Избегаем деления на 0
        panel_width = max(15, self.width // panel_count)

        for i, monster in enumerate(self.enemies):
            panel_x = self.x + i * panel_width
            panel_y = self.y + 1 # Отступ от верхней границы группы
            # Создаем панель, передавая объект Monster
            panel = EnemyUnitPanel(panel_x, panel_y, panel_width - 1, self.height - 2, monster)
            self.panels.append(panel)


class PlayerGroupPanel(GroupPanel):
    """Панель для отображения группы игроков."""

    def __init__(self, x: int, y: int, width: int, height: int, players: List['Player']) -> None:
        """Инициализация панели группы игроков.
        Args:
            x: Координата X.
            y: Координата Y.
            width: Ширина панели.
            height: Высота панели.
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
        # Рассчитываем ширину для каждой панели
        panel_count = len(self.players) if self.players else 1 # Избегаем деления на 0
        panel_width = max(15, self.width // panel_count)

        for i, player in enumerate(self.players):
            panel_x = self.x + i * panel_width
            panel_y = self.y + 1 # Отступ от верхней границы группы
            # Создаем панель, передавая объект Player
            panel = PlayerUnitPanel(panel_x, panel_y, panel_width - 1, self.height - 2, player)
            self.panels.append(panel)


class BattleLog(Renderable):
    """Лог боя в нижней части экрана с прокруткой."""

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
            "Дракон атакует Героя!",
            "Герой увернулся!",
            "Герой атакует Дракон!",
            "Критический удар! Дракон получает 50 урона!",
            "Дракон побежден!",
            "Герой получает 100 опыта."
        ]
        self.scroll_offset: int = 0

    def add_message(self, message: str) -> None:
        """Добавление сообщения в лог.
        Args:
            message: Текст сообщения.
        """
        self.messages.append(message)
        # Автоматически прокручиваем вниз при добавлении нового сообщения
        # (это можно настроить по-разному)
        # self.scroll_offset = max(0, len(self.messages) - self.height)

    def scroll_up(self) -> None:
        """Прокрутка лога вверх."""
        if self.messages:
            self.scroll_offset = max(0, self.scroll_offset - 1)

    def scroll_down(self) -> None:
        """Прокрутка лога вниз."""
        if self.messages:
            max_offset = max(0, len(self.messages) - self.height)
            self.scroll_offset = min(max_offset, self.scroll_offset + 1)

    def update_size(self, total_width: int, total_height: int) -> None:
        """Обновление размеров лога.
        Args:
            total_width: Общая ширина экрана.
            total_height: Общая высота экрана.
        """
        # Занимает всю ширину экрана
        self.width = max(10, total_width - 2) # -2 для отступов

    def render(self, renderer: Renderer) -> None:
        """Отрисовка лога боя."""
        # Отрисовка рамки лога
        renderer.draw_box(self.x, self.y, self.width, self.height)

        # Определяем, какие сообщения отображать с учетом прокрутки
        visible_messages = self.messages[self.scroll_offset:self.scroll_offset + self.height]

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
