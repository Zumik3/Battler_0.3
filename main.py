# main.py

import curses
from game.ui.screen_manager import ScreenManager
# ВАЖНО: Импортируем команды, чтобы они зарегистрировались
import game.ui.commands.inventory_commands
import game.ui.commands.battle_commands
import game.ui.commands.main_screen_commands


def main(stdscr: curses.window) -> None:
    curses.curs_set(0)  # Скрыть курсор
    manager = ScreenManager(stdscr)
    manager.run()


if __name__ == "__main__":
    curses.wrapper(main)
