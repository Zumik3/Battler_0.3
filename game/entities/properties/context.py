# game/entities/properties/context.py
"""Реализация PropertyContext для свойств, использующая GameContext."""

from typing import Any, Optional, TYPE_CHECKING

from game.protocols import PropertyContext

if TYPE_CHECKING:
    from game.core.context import GameContext
    from game.events.bus import EventBus
    from game.config import GameConfig

class GameContextBasedPropertyContext(PropertyContext):
    """PropertyContext, реализованный на основе GameContext."""
    
    def __init__(self, game_context: 'GameContext'):
        """
        Инициализирует контекст свойства.
        
        Args:
            game_context: Экземпляр глобального контекста игры.
        """
        self._game_context = game_context

    @property
    def event_bus(self) -> Optional['EventBus']:
        """Получить доступ к шине событий из глобального контекста."""
        return self._game_context.event_bus

    @property
    def config(self) -> Optional['GameConfig']:
        return self._game_context.config

    def get_service(self, service_name: str) -> Any:
        """Получить доступ к сервису по имени из глобального контекста.
        
        Это упрощенный пример. В реальном проекте здесь может быть
        более сложная логика маршрутизации или фильтрации.
        """
        # Пример: предоставляем доступ к логгеру (если он есть в GameContext)
        # elif service_name == 'logger':
        #     return self._game_context.logger # Предположим, он есть
            
        # Можно предоставить доступ и к самому GameContext, если нужно
        # elif service_name == 'game_context':
        #     return self._game_context
            
        # Для неизвестных сервисов возвращаем None или бросаем исключение
        return None

    def trigger_action(self, action_type: str, data: Any) -> None:
        """Инициировать действие.
        
        В этом примере мы просто печатаем его. В реальном проекте
        здесь будет логика взаимодействия с системой через EventBus
        или напрямую через сервисы из GameContext.
        """
        print(f"[PropertyContext] Action '{action_type}' triggered with data: {data}")
        
        # Пример: публикация специального события через EventBus
        # if self.event_bus:
        #     # Создаем и публикуем специальное событие действия
        #     # action_event = ActionEvent(source=self, action_type=action_type, data=data)
        #     # self.event_bus.publish(action_event)
        #     pass
            
        # Или вызов метода у сервиса из GameContext
        # action_handler = self.get_service('action_handler')
        # if action_handler:
        #     action_handler.handle(action_type, data)
