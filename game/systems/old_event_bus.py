# game/systems/event_bus.py
"""
Система шины событий (Event Bus) для обмена сообщениями между компонентами.

Реализует паттерн publish-subscribe с поддержкой типизации и обработки ошибок.
"""
import sys
from typing import Dict, List, Type, Callable, Any, Tuple, TypeVar, Final
from abc import ABC, abstractmethod

from game.events.event import Event

# Тип для дженериков
T = TypeVar('T', bound=Event)


class IEventBus(ABC):
    """Абстракция шины событий."""
    
    @abstractmethod
    def subscribe(self, source: Any, event_type: Type[T], callback: Callable[[T], None]) -> None:
        """Подписаться на событие определенного типа от конкретного источника."""
        pass
    
    @abstractmethod
    def unsubscribe(self, source: Any, event_type: Type[T], callback: Callable[[T], None]) -> None:
        """Отписаться от события определенного типа от конкретного источника."""
        pass
    
    @abstractmethod
    def publish(self, event: Event) -> None:
        """Опубликовать событие для всех подписчиков."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Очищает всех подписчиков."""
        pass
    
    @abstractmethod
    def get_subscriber_count(self, source: Any, event_type: Type[Event]) -> int:
        """Возвращает количество подписчиков для конкретного источника и типа события."""
        pass
    
    @abstractmethod
    def unsubscribe_all_by_source(self, source: Any) -> None:
        """Удаляет все подписки на указанный источник."""
        pass
    
    @abstractmethod
    def unsubscribe_all_by_callback_owner(self, owner: Any) -> None:
        """Удаляет подписки где callback принадлежит owner."""
        pass


class EventBus(IEventBus):
    """
    Реализация шины событий.
    Используется как синглтон через модульный интерфейс.
    """
    
    def __init__(self) -> None:
        """
        Инициализирует шину событий.
        
        Хранит подписчиков в формате:
        (id(source), event_type) → список callback-функций
        """
        self._subscribers: Dict[Tuple[int, Type[Event]], List[Callable[[Event], None]]] = {}

    def subscribe(
        self, 
        source: Any, 
        event_type: Type[T], 
        callback: Callable[[T], None]
        ) -> None:
        """
        Подписаться на событие определенного типа от конкретного источника.

        Args:
            source: Объект-источник событий.
            event_type: Тип события для подписки.
            callback: Функция-обработчик события.
        """
        key = (id(source), event_type)
        if key not in self._subscribers:
            self._subscribers[key] = []
        
        # Приводим тип для mypy
        typed_callback: Callable[[Event], None] = callback  # type: ignore
        self._subscribers[key].append(typed_callback)

    def unsubscribe(
        self, 
        source: Any, 
        event_type: Type[T], 
        callback: Callable[[T], None]
        ) -> None:
        """
        Отписаться от события определенного типа от конкретного источника.

        Args:
            source: Объект-источник событий.
            event_type: Тип события для отписки.
            callback: Функция-обработчик для удаления.
        """
        key = (id(source), event_type)
        if key in self._subscribers:
            # Приводим тип для mypy
            typed_callback: Callable[[Event], None] = callback  # type: ignore
            
            try:
                self._subscribers[key].remove(typed_callback)
                # Удаляем пустой список подписчиков
                if not self._subscribers[key]:
                    del self._subscribers[key]
            except ValueError:
                # Callback не найден - это нормально
                pass

    # def publish(self, event: Event) -> None:
    #     """
    #     Опубликовать событие для всех подписчиков.

    #     Args:
    #         event: Экземпляр события для публикации.

    #     Raises:
    #         Exception: Любое исключение из обработчиков пробрасывается дальше.
    #     """
    #     source_id = id(event.source) if hasattr(event, 'source') else 0
    #     event_type = type(event)
    #     key = (source_id, event_type)

    #     if key not in self._subscribers:
    #         return

    #     # Работаем с копией для безопасности во время итерации
    #     callbacks = self._subscribers[key][:]
        
    #     for callback in callbacks:
    #         try:
    #             callback(event)
    #         except Exception as error:
    #             self._handle_callback_error(error, event, callback)

    def publish(self, event: Event) -> None:
        source_id = id(event.source) if hasattr(event, 'source') else 0
        event_type = type(event)
        
        # Ищем подписчиков для конкретного типа события
        specific_key = (source_id, event_type)
        if specific_key in self._subscribers:
            self._call_subscribers(specific_key, event)
        
        # Ищем подписчиков для базового класса Event (если event не базовый)
        if event_type != Event:
            base_key = (source_id, Event)
            if base_key in self._subscribers:
                self._call_subscribers(base_key, event)

    def _call_subscribers(self, key: Tuple[int, Type], event: Event):
        """Вызывает подписчиков для конкретного ключа."""
        callbacks = self._subscribers.get(key, [])[:]
        for callback in callbacks:
            try:
                callback(event)
            except Exception as error:
                self._handle_callback_error(error, event, callback)

    def _handle_callback_error(
        self, 
        error: Exception, 
        event: Event, 
        callback: Callable[[Event], None]
        ) -> None:
        """
        Обрабатывает ошибки в обработчиках событий.

        Args:
            error: Пойманное исключение.
            event: Событие, которое обрабатывалось.
            callback: Функция, в которой произошла ошибка.
        """
        source_info = ""
        if hasattr(event, 'source'):
            source = event.source
            source_info = f" от {type(source).__name__}#{id(source)}"
        
        error_msg = (
            f"Ошибка в обработчике события {type(event).__name__}{source_info}\n"
            f"Обработчик: {callback.__name__ if hasattr(callback, '__name__') else callback}\n"
            f"Ошибка: {error}\n"
        )
        
        print(error_msg, file=sys.stderr)
        # Здесь можно добавить логирование в файл
        raise error  # Пробрасываем исключение дальше

    def clear(self) -> None:
        """Очищает всех подписчиков."""
        self._subscribers.clear()

    def get_subscriber_count(self, source: Any, event_type: Type[Event]) -> int:
        """
        Возвращает количество подписчиков для конкретного источника и типа события.

        Args:
            source: Объект-источник.
            event_type: Тип события.

        Returns:
            Количество подписчиков.
        """
        key = (id(source), event_type)
        return len(self._subscribers.get(key, []))

    def unsubscribe_all_by_source(self, source: Any) -> None:
        """Удаляет все подписки на указанный источник."""
        source_id = id(source)
        keys_to_remove = [
            key for key in list(self._subscribers.keys()) 
            if key[0] == source_id
        ]
        for key in keys_to_remove:
            del self._subscribers[key]

    def unsubscribe_all_by_callback_owner(self, owner: Any) -> None:
        """Удаляет подписки где callback принадлежит owner."""
        owner_id = id(owner)
        for key, callbacks in list(self._subscribers.items()):
            # Фильтруем callbacks
            remaining = [
                cb for cb in callbacks 
                if not (hasattr(cb, '__self__') and id(cb.__self__) == owner_id)
            ]
            if remaining:
                self._subscribers[key] = remaining
            else:
                del self._subscribers[key]


# Единственный экземпляр шины на всю игру
_bus_instance: Final[EventBus] = EventBus()


# Публичный API модуля --------------------------------------------------------

def get_event_bus() -> IEventBus:
    """
    Возвращает экземпляр шины событий.
    
    Returns:
        Экземпляр шины событий (абстракция IEventBus).
    """
    return _bus_instance

def subscribe(
    source: Any, 
    event_type: Type[T], 
    callback: Callable[[T], None]
    ) -> None:
    """
    Подписаться на событие определенного типа от конкретного источника.
    
    Args:
        source: Объект-источник событий.
        event_type: Тип события для подписки.
        callback: Функция-обработчик события.
        
    Example:
        >>> from game.events.combat import DamageEvent
        >>> subscribe(player, DamageEvent, on_damage_received)
    """
    _bus_instance.subscribe(source, event_type, callback)

def unsubscribe(
    source: Any, 
    event_type: Type[T], 
    callback: Callable[[T], None]
    ) -> None:
    """
    Отписаться от события определенного типа от конкретного источника.
    
    Args:
        source: Объект-источник событий.
        event_type: Тип события для отписки.
        callback: Функция-обработчик для удаления.
    """
    _bus_instance.unsubscribe(source, event_type, callback)

def publish(event: Event) -> None:
    """
    Опубликовать событие для всех подписчиков.
    
    Args:
        event: Экземпляр события для публикации.
        
    Example:
        >>> from game.events.combat import DamageEvent
        >>> damage_event = DamageEvent(attacker=enemy, target=player, amount=10)
        >>> publish(damage_event)
    """
    _bus_instance.publish(event)

def clear() -> None:
    """Очищает всех подписчиков шины событий."""
    _bus_instance.clear()

def get_subscriber_count(source: Any, event_type: Type[Event]) -> int:
    """
    Возвращает количество подписчиков для конкретного источника и типа события.
    
    Args:
        source: Объект-источник.
        event_type: Тип события.
        
    Returns:
        Количество подписчиков.
    """
    return _bus_instance.get_subscriber_count(source, event_type)

def unsubscribe_all_by_source(source: Any) -> None:
    """Удаляет все подписки на указанный источник."""
    _bus_instance.unsubscribe_all_by_source(source)

def unsubscribe_all_by_callback_owner(owner: Any) -> None:
    """Удаляет подписки где callback принадлежит owner."""
    _bus_instance.unsubscribe_all_by_callback_owner(owner)

# Для отладки и тестирования
def _get_bus_instance() -> EventBus:
    """
    Возвращает внутренний экземпляр шины (только для тестирования!).
    
    Returns:
        Внутренний экземпляр шины событий.
    """
    return _bus_instance