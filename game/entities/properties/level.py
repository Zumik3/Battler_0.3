# game/properties/level.py
"""Свойство уровня персонажа."""

from dataclasses import dataclass, field
from typing import Optional

from game.entities.properties.property import PublishingAndDependentProperty 
from game.events.character import LevelUpEvent, ExperienceGainedEvent
from game.protocols import LevelPropertyProtocol, ExperiencePropertyProtocol # Предполагаемые протоколы


@dataclass
# Наследуемся от PublishingAndDependentProperty
class LevelProperty(PublishingAndDependentProperty, LevelPropertyProtocol): # type: ignore
    """Свойство для управления уровнем персонажа.
    
    Автоматически публикует событие LevelUpEvent при повышении уровня
    и подписывается на события ExperienceGainedEvent для автоматического
    повышения уровня.
    
    Атрибуты:
        level: Текущий уровень персонажа.
        exp_property: Ссылка на свойство опыта для подписки на его события.
                  (добавлено, так как PublishingAndDependentProperty не предоставляет его)
        # Атрибуты context, _is_subscribed наследуются.
    """
    
    level: int = field(default=1)
    exp_property: Optional['ExperiencePropertyProtocol'] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Инициализация свойства уровня."""
        super().__post_init__()
    
    def _setup_subscriptions(self) -> None:
        """Подписывается на события получения опыта."""
        if not self._is_subscribed and self.exp_property and self.context and self.context.event_bus:
            self._subscribe_to(self.exp_property, ExperienceGainedEvent, self._on_experience_gained)
            self._is_subscribed = True
            print(f"  LevelProperty#{id(self)} подписался на ExperienceGainedEvent от Experience#{id(self.exp_property)}")

    def _teardown_subscriptions(self) -> None:
        """Отписывается от событий получения опыта."""
        if self._is_subscribed and self.exp_property and self.context and self.context.event_bus:
            # Отписываемся от события ExperienceGainedEvent 
            # ИСКЛЮЧИТЕЛЬНО от объекта self.exp_property
            self._unsubscribe_from(self.exp_property, ExperienceGainedEvent, self._on_experience_gained)
            self._is_subscribed = False
            print(f"  LevelProperty#{id(self)} отписался от ExperienceGainedEvent от Experience#{id(self.exp_property)}")

    # --- Обработчик события ---
    
    def _on_experience_gained(self, event: ExperienceGainedEvent) -> None:
        """Вызывается при получении события получения опыта."""
        print(f"  LevelProperty#{id(self)} получил событие: {event}")
        # Проверка источника события (на всякий случай, EventBus должен это обеспечить)
        # if event.source is not self.exp_property:
        #     return 
        
        # Здесь должна быть логика проверки, хватает ли опыта для уровня.
        # Для примера предположим, что exp_property предоставляет current_exp и exp_to_level
        # и что для повышения уровня нужно накопить exp_to_level опыта.
        # Также предположим, что exp_to_level увеличивается после каждого уровня.
        # Это очень упрощенная логика, в реальном проекте она может быть сложнее.
        
        # Проверим, что exp_property доступен и имеет нужные атрибуты
        # (в реальном коде это должно быть гарантировано протоколом ExperiencePropertyProtocol)
        if not self.exp_property:
            return
            
        # Пример простой логики: если текущий опыт >= требуемого для уровня
        # Предполагаем, что у exp_property есть атрибуты current_exp и exp_to_level
        # Нужно быть аккуратным с доступом к атрибутам других свойств.
        # Лучше определить это в протоколе ExperiencePropertyProtocol.
        try:
            current_exp = getattr(event, 'current_exp', 0)
            exp_to_level = getattr(event, 'exp_to_level', 100)
            
            if current_exp >= exp_to_level:
                 self.level_up()
                 
        except AttributeError as e:
            # Обработка ошибки доступа к атрибутам exp_property
            print(f"Ошибка доступа к атрибутам exp_property в LevelProperty: {e}")
            # В реальном приложении здесь должно быть логирование
            pass

    # --- Методы управления уровнем ---
    
    def level_up(self, amount: int = 1) -> None:
        """Повышает уровень персонажа и публикует событие.
        
        Returns:
            Список результатов действия (ActionResult), 
            описывающих эффект повышения уровня.
        """
        old_level = self.level
        self.level += amount
        new_level = self.level
        
        self._publish_level_up(old_level, new_level)
    
    def _publish_level_up(self, old_level: int, new_level: int) -> None:
        """Создает и публикует событие повышения уровня."""
        # Проверяем наличие context и event_bus через context
        if self.context and hasattr(self.context, 'event_bus') and self.context.event_bus:
            # Создаем событие, используя self как источник
            event = LevelUpEvent(
                source=self,
                old_level=old_level,
                new_level=new_level
            )
            # Используем метод _publish из миксина PublisherPropertyMixin
            self._publish(event)

    def get_level(self) -> int:
        """Возвращает текущий уровень.
        
        Returns:
            Текущий уровень персонажа.
        """
        return self.level
