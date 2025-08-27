# game/ui/screen_manager.py
"""Управление экранами игры.
Реализует паттерн Состояние для переключения между экранами."""

import curses
from typing import Dict, Type, List, TYPE_CHECKING

from game.ui.base_screen import BaseScreen
from game.ui.battle_screen import BattleScreen
from game.ui.inventory_screen import InventoryScreen
from game.ui.main_screen import MainScreen
from game.ui.rendering.color_manager import ColorManager
from game.ui.rendering.renderer import Renderer

# Импортируем GameManager только для аннотаций типов, чтобы избежать циклических импортов
if TYPE_CHECKING:
    from game.game_manager import GameManager


class ScreenManager:
    """Управление экранами игры с использованием паттерна состояние."""

    def __init__(self, stdscr: curses.window, game_manager: 'GameManager') -> None:
        """
        Инициализация менеджера экранов.

        Args:
            stdscr: Окно curses.
            game_manager: Экземпляр GameManager, содержащий все игровые сущности.
        """
        self.stdscr = stdscr
        self.game_manager = game_manager # Сохраняем ссылку на GameManager
        self.running = True

        self.color_manager = ColorManager()
        self.color_manager.initialize(stdscr)

        # Инициализируем renderer, он получит начальный размер
        self.renderer = Renderer(stdscr, self.color_manager)

        # Словарь доступных экранов (имя -> класс)
        self.screens: Dict[str, Type[BaseScreen]] = {
            "main": MainScreen,
            "battle": BattleScreen,
            "inventory": InventoryScreen,
        }

        # Стек экранов для управления историей переходов
        self.screen_stack: List[BaseScreen] = []

        # Начинаем с главного экрана, передаем ему ссылку на себя (manager)
        initial_screen = self.screens["main"](self)
        self.screen_stack.append(initial_screen)

    @property
    def current_screen(self) -> BaseScreen:
        """Текущий экран - верхний элемент стека."""
        return self.screen_stack[-1]

    def stop(self) -> None:
        """Останавливает основной цикл менеджера экранов."""
        self.running = False

    def change_screen(self, screen_name: str) -> None:
        """Переход на новый экран (добавление в стек).

        Args:
            screen_name: Имя экрана для перехода.
        """
        if screen_name in self.screens:
            # Создаем новый экран, передавая ему ссылку на ScreenManager (self)
            new_screen = self.screens[screen_name](self)
            self.screen_stack.append(new_screen)
        else:
            raise ValueError(f"Неизвестный экран: {screen_name}")

    def go_back(self) -> None:
        """Возврат к предыдущему экрану (выход из стека)."""
        if len(self.screen_stack) > 1:
            self.screen_stack.pop()
        else:
            self.stop()

    def _update_renderer_for_all_screens(self) -> None:
        """Обновляет renderer для всех экранов в стеке."""
        # Создаём НОВЫЙ экземпляр renderer с текущими размерами stdscr
        # curses.update_lines_cols() не всегда нужно, зависит от терминала
        height, width = self.stdscr.getmaxyx()
        
        # ВАЖНО: Создаем новый экземпляр Renderer, а не пытаемся обновить старый
        self.renderer = Renderer(self.stdscr, self.color_manager)
        # Примечание: Вызов update_size(width, height) не нужен, так как
        # конструктор Renderer уже должен получить размеры из stdscr.

        # Передаём новый renderer всем экранам в стеке
        for screen in self.screen_stack:
            screen.renderer = self.renderer

    def run(self) -> None:
        """Основной цикл работы менеджера экранов."""
        while self.running:
            # Получаем текущий экран
            current = self.current_screen

            # Обновляем размеры renderer, если размер окна изменился
            # curses.update_lines_cols() не всегда нужно, зависит от терминала
            height, width = self.stdscr.getmaxyx()
            # Сравниваем с размерами, которые знает renderer
            # Предполагается, что у renderer есть атрибуты width и height,
            # установленные в его __init__
            if hasattr(self.renderer, 'height') and hasattr(self.renderer, 'width'):
                 # Если эти атрибуты есть и отличаются
                 if height != self.renderer.height or width != self.renderer.width:
                     self._update_renderer_for_all_screens()
            else:
                 # Если атрибутов нет, обновляем на всякий случай
                 # или предполагаем, что они устанавливаются в __init__
                 # Возможно, нужно добавить их установку в __init__ Renderer
                 self._update_renderer_for_all_screens()

            # Отрисовываем текущий экран
            current.render(self.stdscr)

            # Обновляем экран
            self.stdscr.refresh()

            # Получаем ввод пользователя
            try:
                key = self.stdscr.getch()
                # Обрабатываем ввод
                current.handle_input(key)
            except KeyboardInterrupt:
                self.stop()
            except Exception as e:
                # Логирование или обработка других исключений
                # Пока просто выходим
                print(f"Критическая ошибка: {e}")
                self.stop()
