# game/core/context.py
"""Игровой контекст - центральный хаб для всех сервисов."""

from dataclasses import dataclass, field
from typing import Optional
from game.config import GameConfig
from game.events.bus import EventBus


@dataclass
class GameContext:
    """Контекст игры со всеми необходимыми сервисами."""
    
    config: GameConfig
    # EventBus обязателен, убираем Optional и __post_init__ упрощает логику
    event_bus: EventBus 

# ContextFactory тоже остается, но немного упрощается
class ContextFactory:
    """Фабрика для создания игрового контекста."""
    
    @staticmethod
    def create_default_context(config: Optional[GameConfig] = None) -> GameContext:
        """Создает контекст с настройками по умолчанию."""
        if config is None:
            from game.config import get_config
            config = get_config()
        
        event_bus = EventBus()
        
        # Теперь event_bus гарантированно передается
        return GameContext(
            config=config,
            event_bus=event_bus
        )
