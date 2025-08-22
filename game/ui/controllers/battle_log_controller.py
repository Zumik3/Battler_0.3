"""Контроллер для управления логом боя и обработки событий.

Обеспечивает связь между системой событий игры и визуальным компонентом BattleLog.
Автоматически подписывается на события и отображает их в UI боя.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from game.events.combat import DamageEvent, DeathEvent, LogUpdatedEvent
from game.events.event import Event
from game.systems.event_bus import HIGH_PRIORITY

if TYPE_CHECKING:
    from game.ui.components.battle_components import BattleLog
    from game.systems.event_bus import EventBus


class BattleLogController:
    """Контроллер для работы BattleLog с событиями боя.
    
    Attributes:
        battle_log: Визуальный компонент для отображения сообщений
        _is_active: Флаг активности контроллера
        _event_bus: Шина событий для подписки/отписки
    """
    
    def __init__(self, event_bus: 'EventBus', battle_log: 'BattleLog') -> None:
        """Инициализирует контроллер лога боя.
        
        Args:
            context: Игровой контекст с доступом к шине событий
            battle_log: Визуальный компонент для отображения сообщений
        """
        self.battle_log = battle_log
        self._is_active = False
        self._event_bus = event_bus
    
    def activate(self) -> None:
        """Активирует контроллер - подписывается на события напрямую."""
        if not self._is_active:
            self._event_bus.subscribe(None, Event, self._handle_event)
            self._is_active = True
    
    def deactivate(self) -> None:
        """Деактивирует контроллер - отписывается от событий."""
        if self._is_active:
            try:
                self._event_bus.unsubscribe(None, Event, self._handle_event)
                self._is_active = False
            except Exception as e:
                # Логирование ошибки отписки можно добавить при необходимости
                pass
    
    def _handle_event(self, event: Event) -> None:
        """Обрабатывает событие и добавляет в лог.
        
        Args:
            event: Событие для обработки
        """
        try:
            if hasattr(event, 'render_data') and event.render_data:
                self.battle_log.add_message(event.render_data)
                self._render_battle_screen()
        except Exception as e:
            # Обработка ошибок добавления сообщения в лог
            pass

    def _render_battle_screen(self) -> None:
        self._event_bus.publish(LogUpdatedEvent(source=None, need_render=True))