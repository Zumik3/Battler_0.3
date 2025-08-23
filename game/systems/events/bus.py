# game/systems/event_bus.py
"""
Система шины событий (Event Bus) для обмена сообщениями между компонентами.

Реализует паттерн publish-subscribe с поддержкой типизации, обработки ошибок и приоритетов.
"""
import sys
from typing import Dict, List, Type, Callable, Any, Tuple, TypeVar, Final
from abc import ABC, abstractmethod
import heapq

from game.events.event import Event

# --- НАЧАЛО ИЗМЕНЕНИЙ: Определение приоритетов ---
# Константы для приоритетов (меньшее число = более высокий приоритет)
HIGH_PRIORITY: Final[int] = 0
NORMAL_PRIORITY: Final[int] = 10
LOW_PRIORITY: Final[int] = 20
# --- КОНЕЦ ИЗМЕНЕНИЙ ---

# Тип для дженериков
T = TypeVar('T', bound=Event)

# --- НАЧАЛО ИЗМЕНЕНИЙ: Тип для хранения подписчика с приоритетом ---
# Храним кортеж (приоритет, callback) для каждого подписчика
SubscriberEntry = Tuple[int, Callable[[Event], None]]
# --- КОНЕЦ ИЗМЕНЕНИЙ ---


class IEventBus(ABC):
    """Абстракция шины событий."""
    
    @abstractmethod
    def subscribe(self, source: Any, event_type: Type[T], callback: Callable[[T], None], priority: int = NORMAL_PRIORITY) -> None:
        """
        Подписаться на событие определенного типа от конкретного источника.
        
        Args:
            source: Объект-источник событий.
            event_type: Тип события для подписки.
            callback: Функция-обработчик события.
            priority: Приоритет обработчика (меньше значение = выше приоритет).
                      По умолчанию NORMAL_PRIORITY.
        """
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
    Реализация шины событий с поддержкой приоритетов.
    Используется как синглтон через модульный интерфейс.
    """
    
    def __init__(self) -> None:
        """
        Инициализирует шину событий.
        
        Хранит подписчиков в формате:
        (id(source), event_type) → список (приоритет, callback)-кортежей
        """
        # --- НАЧАЛО ИЗМЕНЕНИЙ: Изменен тип значения в словаре ---
        self._subscribers: Dict[Tuple[int, Type[Event]], List[SubscriberEntry]] = {}
        # --- КОНЕЦ ИЗМЕНЕНИЙ ---

    def subscribe(
        self, 
        source: Any, 
        event_type: Type[T], 
        callback: Callable[[T], None],
        priority: int = NORMAL_PRIORITY
        ) -> None:
        """
        Подписаться на событие определенного типа от конкретного источника.

        Args:
            source: Объект-источник событий.
            event_type: Тип события для подписки.
            callback: Функция-обработчик события.
            priority: Приоритет обработчика (меньше значение = выше приоритет).
                      По умолчанию NORMAL_PRIORITY.
        """
        key = (id(source), event_type)
        if key not in self._subscribers:
            self._subscribers[key] = []
        
        # --- НАЧАЛО ИЗМЕНЕНИЙ: Сохраняем приоритет вместе с callback ---
        # Приводим тип для mypy
        typed_callback: Callable[[Event], None] = callback  # type: ignore
        # Добавляем кортеж (приоритет, callback)
        self._subscribers[key].append((priority, typed_callback))
        # --- КОНЕЦ ИЗМЕНЕНИЙ ---

    # Метод unsubscribe остается без изменений, так как он ищет callback по ссылке
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
            # --- НАЧАЛО ИЗМЕНЕНИЙ: Ищем callback внутри кортежа (приоритет, callback) ---
            # Приводим тип для mypy
            typed_callback: Callable[[Event], None] = callback  # type: ignore
            
            try:
                # Находим и удаляем кортеж, где второй элемент (callback) совпадает
                self._subscribers[key] = [
                    entry for entry in self._subscribers[key] 
                    if entry[1] != typed_callback
                ]
                # Удаляем пустой список подписчиков
                if not self._subscribers[key]:
                    del self._subscribers[key]
            except ValueError:
                # Callback не найден - это нормально
                pass
            # --- КОНЕЦ ИЗМЕНЕНИЙ ---

    def publish(self, event: Event) -> None:
        """
        Опубликовать событие для всех подписчиков.
        Объединяет подписчиков на конкретный тип и на Event, затем сортирует по приоритету.
        """
        source_id = id(event.source) if hasattr(event, 'source') else 0
        event_type = type(event)
        
        all_entries_to_call: List[SubscriberEntry] = []

        specific_key = (source_id, event_type)
        if specific_key in self._subscribers:
            all_entries_to_call.extend(self._subscribers[specific_key])

        if event_type != Event:
            base_key = (source_id, Event)
            if base_key in self._subscribers:
                all_entries_to_call.extend(self._subscribers[base_key])

        if all_entries_to_call:
            sorted_entries = sorted(all_entries_to_call, key=lambda entry: entry[0])
            
            for priority, callback in sorted_entries:
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
        for key, entries in list(self._subscribers.items()):
            # --- НАЧАЛО ИЗМЕНЕНИЙ: Фильтруем по callback внутри кортежа ---
            remaining = [
                entry for entry in entries 
                if not (hasattr(entry[1], '__self__') and id(entry[1].__self__) == owner_id)
            ]
            if remaining:
                self._subscribers[key] = remaining
            else:
                del self._subscribers[key]
            # --- КОНЕЦ ИЗМЕНЕНИЙ ---


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

# --- НАЧАЛО ИЗМЕНЕНИЙ: Добавлен параметр priority со значением по умолчанию ---
def subscribe(
    source: Any, 
    event_type: Type[T], 
    callback: Callable[[T], None],
    priority: int = NORMAL_PRIORITY
    ) -> None:
    """
    Подписаться на событие определенного типа от конкретного источника.
    
    Args:
        source: Объект-источник событий.
        event_type: Тип события для подписки.
        callback: Функция-обработчик события.
        priority: Приоритет обработчика (меньше значение = выше приоритет).
                  По умолчанию NORMAL_PRIORITY.
        
    Example:
        >>> from game.events.combat import DamageEvent
        >>> subscribe(player, DamageEvent, on_damage_received, priority=HIGH_PRIORITY)
    """
    _bus_instance.subscribe(source, event_type, callback, priority)
# --- КОНЕЦ ИЗМЕНЕНИЙ ---

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
