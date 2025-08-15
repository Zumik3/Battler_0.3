# game/ui/commands/__init__.py
"""
Пакет конкретных команд для разных экранов.

Содержит реализации команд для конкретных экранов игры.
"""

# ВАЖНО: Импортируем все команды, чтобы они зарегистрировались
import game.ui.commands.common_commands
import game.ui.commands.inventory_commands
import game.ui.commands.battle_commands
import game.ui.commands.main_screen_commands

# Экспортируем основные классы команд для удобства использования
# Общие команды
from .common_commands import (
    GoBackCommand,
    OpenInventoryCommand,
    HelpCommand,
    ExitCommand
)

# Специфические команды инвентаря
from .inventory_commands import (
    UseItemCommand,
    DropItemCommand
)

# Специфические команды боя
from .battle_commands import (
    AttackCommand,
    DefendCommand,
    MagicCommand as BattleMagicCommand
)

# Специфические команды главного экрана
from .main_screen_commands import (
    StartBattleCommand,
    OpenSettingsCommand
)

__all__ = [
    # Общие команды
    'GoBackCommand',
    'OpenInventoryCommand',
    'HelpCommand',
    'ExitCommand',
    
    # Команды инвентаря
    'UseItemCommand',
    'DropItemCommand',
    
    # Команды боя
    'AttackCommand',
    'DefendCommand',
    'BattleMagicCommand',
    
    # Команды главного экрана
    'StartBattleCommand',
    'OpenSettingsCommand'
]