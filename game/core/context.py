# game/core/context.py
"""Игровой контекст - центральный хаб для всех сервисов."""

from dataclasses import dataclass
from typing import Optional
from game.config import GameConfig
from game.events.bus import EventBus


@dataclass
class GameContext:
    """Контекст игры со всеми необходимыми сервисами."""
    
    config: GameConfig
    event_bus: EventBus
    
    def __post_init__(self):
        """Инициализация контекста."""
        if self.event_bus is None:
            self.event_bus = EventBus()


class ContextFactory:
    """Фабрика для создания игрового контекста."""
    
    @staticmethod
    def create_default_context(config: Optional[GameConfig] = None) -> GameContext:
        """Создает контекст с настройками по умолчанию."""
        if config is None:
            from game.config import get_config
            config = get_config()
        
        event_bus = EventBus()
        
        return GameContext(
            config=config,
            event_bus=event_bus
        )