# game/core/game_context.py
"""Игровой контекст - центральный хаб для всех сервисов."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from game.config import GameConfig
from game.systems.combat.ability_registry import AbilityRegistry
from game.systems.events.bus import IEventBus

if TYPE_CHECKING:
    from game.protocols import AbilityRegistryProtocol

@dataclass
class GameContext:
    """Контекст игры со всеми необходимыми сервисами."""
    
    config: GameConfig
    event_bus: IEventBus
    ability_registry: 'AbilityRegistryProtocol'


class ContextFactory:
    """Фабрика для создания игрового контекста."""
    
    @staticmethod
    def create_default_context(config: Optional[GameConfig] = None) -> GameContext:
        """
        Создает контекст с настройками по умолчанию.
        
        Args:
            config: Конфигурация игры. Если None, используется конфигурация по умолчанию.
            
        Returns:
            Инициализированный игровой контекст.
        """
        if config is None:
            from game.config import get_config
            config = get_config()
        
        # Получаем синглтон через публичный интерфейс
        from game.systems.events.bus import get_event_bus
        event_bus = get_event_bus()
        ability_registry = AbilityRegistry()

        return GameContext(
            config=config,
            event_bus=event_bus,
            ability_registry=ability_registry
        )