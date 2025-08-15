# game/ui/screen_manager.py
import curses
from typing import Dict, Type, List
from game.ui.base_screen import BaseScreen
from game.ui.main_screen import MainScreen
from game.ui.battle_screen import BattleScreen
from game.ui.inventory_screen import InventoryScreen
from game.ui.rendering.renderer import Renderer
from game.ui.rendering.color_manager import ColorManager

class ScreenManager:
    """Управление экранами игры с использованием паттерна состояние."""
    def __init__(self, stdscr: curses.window):
        self.stdscr = stdscr
        self.color_manager = ColorManager()
        self.color_manager.initialize(stdscr)
        # Инициализируем renderer, он получит начальный размер
        self.renderer = Renderer(stdscr, self.color_manager)
        self.screens: Dict[str, Type[BaseScreen]] = {
            "main": MainScreen,
            "battle": BattleScreen,
            "inventory": InventoryScreen,
        }
        self.screen_stack: List[BaseScreen] = []
        # Начинаем с главного экрана
        initial_screen = self.screens["main"](self)
        self.screen_stack.append(initial_screen)

    @property
    def current_screen(self) -> BaseScreen:
        """Текущий экран - верхний элемент стека."""
        return self.screen_stack[-1]

    def change_screen(self, screen_name: str) -> None:
        """Переход на новый экран (добавление в стек)."""
        if screen_name in self.screens:
            new_screen = self.screens[screen_name](self)
            self.screen_stack.append(new_screen)
        else:
            raise ValueError(f"Неизвестный экран: {screen_name}")

    def go_back(self) -> None:
        """Возврат к предыдущему экрану (выход из стека)."""
        if len(self.screen_stack) > 1:
            self.screen_stack.pop()
        else:
            # Если это последний экран - выходим из приложения
            exit()

    def _update_renderer_for_all_screens(self) -> None:
        """Обновляет renderer для всех экранов в стеке."""
        # Создаём новый экземпляр renderer с текущими размерами stdscr
        self.renderer = Renderer(self.stdscr, self.color_manager)
        # Обновляем renderer у всех экранов в стеке
        for screen in self.screen_stack:
            screen.renderer = self.renderer # type: ignore # BaseScreen.renderer аннотирован как Renderer

    def run(self) -> None:
        """Основной цикл отображения текущего экрана."""
        while True:
            self.current_screen.render(self.stdscr)
            key = self.stdscr.getch()

            # Проверяем, является ли нажатая клавиша сигналом изменения размера
            if key == curses.KEY_RESIZE:
                # Сообщаем curses об изменении размера (иногда помогает)
                # h, w = self.stdscr.getmaxyx() # Не всегда нужно, но можно попробовать
                # curses.resizeterm(h, w) # Не всегда нужно, но можно попробовать

                # Обновляем renderer у менеджера и всех экранов
                self._update_renderer_for_all_screens()
                # Продолжаем цикл для перерисовки с новым renderer'ом
                continue # Переход к следующей итерации цикла, что вызовет перерисовку

            # Если это не изменение размера, обрабатываем ввод как обычно
            self.current_screen.handle_input(key)
