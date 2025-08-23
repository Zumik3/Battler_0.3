# game/core/context.py
"""Игровой контекст - центральный хаб для всех сервисов."""

from dataclasses import dataclass
from typing import Optional

from game.config import GameConfig
from game.systems.events.bus import IEventBus


@dataclass
class GameContext:
    """Контекст игры со всеми необходимыми сервисами."""
    
    config: GameConfig
    event_bus: IEventBus


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
        
        return GameContext(
            config=config,
            event_bus=event_bus
        )