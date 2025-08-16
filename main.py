# main.py
import curses
from game.ui import ScreenManager
from game.game_manager import get_game_manager

# ВАЖНО: Импортируем команды, чтобы они зарегистрировались
import game.ui.commands.inventory_commands
import game.ui.commands.battle_commands
import game.ui.commands.main_screen_commands


def main(stdscr: curses.window) -> None:
    """Главная функция curses приложения."""
    curses.curs_set(0) # Скрыть курсор

    # --- Инициализация игрового состояния ---
    game_manager = get_game_manager()

    # --- Инициализация менеджера экранов с группой игроков ---
    manager = ScreenManager(stdscr, game_manager)
    manager.run()


if __name__ == "__main__":
    curses.wrapper(main)
