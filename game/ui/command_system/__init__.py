# game/ui/command_system/__init__.py
"""
Система команд пользовательского интерфейса.

Содержит самодостаточные команды и систему их регистрации.
"""

from .command import Command, CommandRegistry
from .screen_command_registry import (
    register_screen_commands,
    get_screen_commands,
    get_all_registered_screens,
    clear_registry
)
from .command_renderer import CommandRenderer  # ДОБАВИЛИ!

__all__ = [
    'Command',
    'CommandRegistry',
    'CommandRenderer',  # ДОБАВИЛИ!
    'register_screen_commands',
    'get_screen_commands',
    'get_all_registered_screens',
    'clear_registry'
]