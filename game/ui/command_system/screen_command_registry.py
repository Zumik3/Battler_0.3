# game/ui/command_system/screen_command_registry.py
"""
Реестр команд для экранов.

Реализует паттерн Реестр для хранения связей между экранами и их командами.
"""

from typing import Dict, List, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from game.ui.base_screen import BaseScreen
    from game.ui.command_system.command import Command

# Глобальный реестр: КлассЭкрана -> СписокКоманд
SCREEN_COMMANDS: Dict[Type['BaseScreen'], List['Command']] = {}


def register_screen_commands(screen_class: Type['BaseScreen'], commands: List['Command']) -> None:
    """
    Регистрация команд для конкретного экрана.
    
    Args:
        screen_class: Класс экрана
        commands: Список команд для этого экрана
    """
    SCREEN_COMMANDS[screen_class] = commands


def get_screen_commands(screen_class: Type['BaseScreen']) -> List['Command']:
    """
    Получение команд для конкретного экрана.
    
    Args:
        screen_class: Класс экрана
        
    Returns:
        Список команд для экрана (пустой список если нет команд)
    """
    return SCREEN_COMMANDS.get(screen_class, [])


def get_all_registered_screens() -> List[Type['BaseScreen']]:
    """
    Получение всех экранов с зарегистрированными командами.
    
    Returns:
        Список классов экранов
    """
    return list(SCREEN_COMMANDS.keys())


def clear_registry() -> None:
    """Очистка реестра (для тестирования)."""
    SCREEN_COMMANDS.clear()