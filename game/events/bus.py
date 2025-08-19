# game/events/bus.py
"""Шина событий игры."""

import sys
from typing import Dict, Generic, List, Callable, Type, TypeVar, Any, Tuple
from dataclasses import dataclass

T = TypeVar('T', bound='Event')
TSource = TypeVar('TSource')


@dataclass
class Event(Generic[TSource]):
    """Базовый класс для всех событий с указанием источника.

    Атрибуты:
        source: Объект, который инициировал событие.
    """
    source: TSource
    """Объект, который инициировал событие."""


class EventBus:
    """Шина событий для обмена сообщениями между компонентами.

    Позволяет подписываться на события от конкретных источников,
    обеспечивая точечную доставку сообщений.
    """

    def __init__(self) -> None:
        """Инициализирует шину событий."""
        # Ключ: кортеж (id объекта-источника, тип события)
        # Значение: список callback-функций
        # Используем id(source) вместо source, чтобы избежать проблем 
        # с хешируемостью объектов-источников
        self._subscribers: Dict[Tuple[int, Type[Event]], List[Callable]] = {}

    def subscribe(
        self, 
        source: Any, 
        event_type: Type[T], 
        callback: Callable[[T], None]
    ) -> None:
        """Подписаться на событие определенного типа от конкретного источника.

        Args:
            source: Объект, от которого ожидается событие.
            event_type: Тип события, на которое производится подписка.
            callback: Функция обратного вызова, которая будет вызвана
                      при публикации события указанного типа от указанного 
                      источника.
        """
        # Используем id(source) для создания хешируемого ключа
        key = (id(source), event_type)
        if key not in self._subscribers:
            self._subscribers[key] = []
        self._subscribers[key].append(callback)

        # debug
        # print(f"{source.__class__} подписался на {key} - callback {callback}")

    def unsubscribe(
        self, 
        source: Any, 
        event_type: Type[T], 
        callback: Callable[[T], None]
    ) -> None:
        """Отписаться от события.

        Args:
            source: Объект-источник.
            event_type: Тип события.
            callback: Функция обратного вызова, от которой нужно отписаться.
        """
        key = (id(source), event_type)
        if key in self._subscribers:
            try:
                self._subscribers[key].remove(callback)
                # Если список подписчиков пуст, удаляем ключ
                if not self._subscribers[key]:
                    del self._subscribers[key]
            except ValueError:
                # Callback не найден в списке, ничего не делаем
                pass

    def publish(self, event: Event) -> None:
        """Опубликовать событие.

        Вызывает все зарегистрированные обработчики (callback-функции)
        для пары (id(event.source), type(event)). Ошибки в обработчиках
        логируются, и исключение пробрасывается дальше, прерывая обработку.

        Args:
            event: Экземпляр события для публикации.

        Raises:
            Exception: Любое исключение, возникшее в обработчике события.
        """
        # Используем id(event.source) для поиска подписчиков
        source_id = id(event.source)
        event_type = type(event)
        key = (source_id, event_type)

        if key in self._subscribers:
            # Итерируемся по копии списка, чтобы избежать проблем
            # при модификации списка подписчиков во время итерации
            for callback in self._subscribers[key][:]:
                try:
                    callback(event)
                except Exception as e:
                    # Выводим сообщение об ошибке, включая информацию об 
                    # источнике
                    print(
                        f"Ошибка в обработчике события {event_type.__name__} "
                        f"от источника {type(event.source).__name__}#{source_id} "
                        f"при вызове {callback}: {e}",
                        file=sys.stderr
                    )
                    # Прерываем обработку события и пробрасываем исключение
                    raise
