# main.py
"""Главная точка входа в игру."""

import curses
import sys
import traceback

from game.ui import ScreenManager
from game.game_manager import get_game_manager

# ВАЖНО: Импортируем команды, чтобы они зарегистрировались
import game.ui.commands.inventory_commands
import game.ui.commands.battle_commands
import game.ui.commands.main_screen_commands


def main(stdscr: curses.window) -> None:
    """Главная функция curses приложения."""
    try:
        # Настройка curses
        curses.curs_set(0)  # Скрыть курсор
        stdscr.keypad(True)  # Включить обработку специальных клавиш
        
        # Инициализация игрового состояния
        game_manager = get_game_manager()
        
        # Инициализация менеджера экранов
        manager = ScreenManager(stdscr, game_manager)
        manager.run()
        
    except KeyboardInterrupt:
        # Корректный выход по Ctrl+C
        pass
    except Exception as e:
        # Обработка критических ошибок
        curses.endwin()
        print(f"Критическая ошибка: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except Exception as e:
        # Эта обработка сработает, если ошибка произойдет вне `main`
        # или если curses.wrapper не сможет ее корректно обработать.
        print("--- КРИТИЧЕСКАЯ ОШИБКА ВНЕ ОСНОВНОГО ЦИКЛА ---")
        import traceback
        traceback.print_exc()
        print("-------------------------------------------------")