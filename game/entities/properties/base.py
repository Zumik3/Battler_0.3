# game/properties/base.py
"""Базовые классы для свойств."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, List, NamedTuple, Optional, Protocol, Type

if TYPE_CHECKING:
    # Импорты, используемые только для аннотаций типов
    from game.events.event import Event # Используется в миксинах
    from game.protocols import PropertyContext


class HasContext(Protocol):
    """Протокол, описывающий класс, который предоставляет контекст свойства."""

    @property
    def context(self) -> Optional['PropertyContext']:
        """Получить контекст свойства."""
        # В протоколе тело метода/свойства обычно пустое (...)
        pass


class SubscriptionData(NamedTuple):
    """Контейнер для данных подписки с строгим порядком."""
    source: Any
    event_type: Type['Event']
    callback: Callable


# --- Базовые классы и миксины ---

@dataclass
class BaseProperty:
    """Базовый dataclass для всех свойств."""
    context: 'PropertyContext'


class SubscriberPropertyMixin:
    """Миксин для свойств, которые подписываются на события."""
    # Предполагаем, что _is_subscribed будет определен в классе-потребителе
    _is_subscribed: bool 
    
    def _subscribe_to(self: HasContext, source: Any, event_type: Type['Event'], callback: Callable) -> None:
        """Подписаться на событие от конкретного источника."""
        # Используем прямой доступ, так как context определен в BaseProperty
        if self.context and self.context.event_bus:
            self.context.event_bus.subscribe(source, event_type, callback)
            
    def _unsubscribe_from(self: HasContext, source: Any, event_type: Type['Event'], callback: Callable) -> None:
        """Отписаться от события от конкретного источника."""
        if self.context and self.context.event_bus:
            self.context.event_bus.unsubscribe(source, event_type, callback)


class PublisherPropertyMixin:
    """Миксин для свойств, которые публикуют события."""
    
    def _publish(self: HasContext, event: 'Event') -> None:
        """Опубликовать событие."""
        if self.context and self.context.event_bus:
            self.context.event_bus.publish(event)


class SubscriptionLifecycleMixin:
    """Миксин для управления жизненным циклом подписок.
    
    Предоставляет методы для инициализации, очистки и отслеживания состояния подписки.
    Предполагает наличие атрибута `_is_subscribed`.
    """
    _is_subscribed: bool
    
    def _setup_subscriptions(self) -> None:
        """Настраивает подписки. Должен быть реализован в подклассах."""
        raise NotImplementedError(
            f"Класс {self.__class__.__name__} должен реализовать _setup_subscriptions"
        )
        
    def _teardown_subscriptions(self) -> None:
        """Отписывается. Должен быть реализован в подклассах."""
        raise NotImplementedError(
            f"Класс {self.__class__.__name__} должен реализовать _teardown_subscriptions"
        )

    def cleanup(self) -> None:
        """Отписывается от всех наблюдателей."""
        if getattr(self, '_is_subscribed', False): 
            self._teardown_subscriptions()

    def subscribe(self) -> None:
        if not getattr(self, '_is_subscribed', True):
            self._setup_subscriptions()


@dataclass
class DependentProperty(BaseProperty, SubscriberPropertyMixin, SubscriptionLifecycleMixin):
    """Базовый dataclass для свойств, зависящих от событий.
    
    Управляет подпиской на события через EventBus. Подклассы должны
    реализовать методы _setup_subscriptions и _teardown_subscriptions.
    """
    _is_subscribed: bool = field(default=False)
    _subscriptions: List['SubscriptionData'] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        self._setup_subscriptions()

    def _teardown_subscriptions(self) -> None:
        """Отписывается от изменений статов."""
        if self._is_subscribed and self.context:
            for source, event_type, callback in self._subscriptions:
                self._unsubscribe_from(source, event_type, callback)
            self._is_subscribed = False

@dataclass
class PublishingProperty(BaseProperty, PublisherPropertyMixin):
    """Свойство, которое публикует события."""
    # Дополнительная логика, если нужна, может быть добавлена в подклассах
    pass


@dataclass
class PublishingAndDependentProperty(
    BaseProperty, 
    SubscriberPropertyMixin, 
    PublisherPropertyMixin, 
    SubscriptionLifecycleMixin
    ):
    """Свойство, которое и подписывается на события, и публикует их."""
    _is_subscribed: bool = field(default=False)
    
    def __post_init__(self) -> None:
        """Инициализация после создания."""
        self._setup_subscriptions()
