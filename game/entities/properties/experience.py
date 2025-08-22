# game/entities/properties/experience.py
"""Свойство опыта персонажа."""

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

# Импортируем событие наград, которое будем обрабатывать
from game.events.reward_events import RewardExperienceGainedEvent

from game.entities.properties.base import PublishingAndDependentProperty 
from game.events.character import ExperienceGainedEvent, LevelUpEvent
from game.protocols import ExperienceSystemProtocol
from game.entities.properties.level import LevelProperty

# Для отложенного импорта в функции регистрации
if TYPE_CHECKING:
    from game.core.context import GameContext

@dataclass
class ExperienceProperty(PublishingAndDependentProperty, ExperienceSystemProtocol): 
    """Свойство для управления опытом персонажа.
    
    Автоматически публикует событие ExperienceGainedEvent при получении опыта
    и подписывается на события LevelUpEvent для обновления требований опыта.
    
    Атрибуты:
        exp_to_level: Количество опыта, необходимое для следующего уровня.
        current_exp: Текущее количество накопленного опыта.
        level_property: Ссылка на свойство уровня для подписки на его события.
        # Атрибуты context, _is_subscribed наследуются от PublishingAndDependentProperty.
    """
    
    exp_to_level: int = field(default=100) # Пример начального значения
    current_exp: int = field(default=0)
    level_property: Optional['LevelProperty'] = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Инициализация свойства опыта."""
        # Вызываем __post_init__ базового класса, который вызовет _setup_subscriptions
        super().__post_init__()
        
        if self.current_exp < 0:
            self.current_exp = 0
            
        # После инициализации подписок, убедимся, что состояние exp корректно
        # относительно начального уровня (если level_property уже задан).
        # Это может быть избыточно, если логика уровней строго последовательна,
        # но добавляет надежности.
        # self._adjust_exp_after_level_up() # Можно вызвать, если нужно
    
    def _setup_subscriptions(self) -> None:
        """Подписывается на события повышения уровня."""
        # Проверяем зависимости
        if not self._is_subscribed and self.level_property and self.context and self.context.event_bus:
            self._subscribe_to(self.level_property, LevelUpEvent, self._on_level_up)
            self._is_subscribed = True
            # print(f"  ExpProperty#{id(self)} подписался на LevelUpEvent от Level#{id(self.level_property)}")
            
    def _teardown_subscriptions(self) -> None:
        """Отписывается от событий повышения уровня."""
        if self._is_subscribed and self.level_property and self.context and self.context.event_bus:
            self._unsubscribe_from(self.level_property, LevelUpEvent, self._on_level_up)
            self._is_subscribed = False
            
    # --- Обработчик события ---
    
    def _on_level_up(self, event: LevelUpEvent) -> None:
        """Вызывается при получении события повышения уровня.
        
        Сбрасывает текущий опыт, обрезая то количество, которое "забрало" 
        повышение уровня, и обновляет требование опыта на следующий уровень.
        """  
        # Логика обрезки опыта:
        # 1. Вычисляем, сколько опыта было "потрачено" на уровень.
        #    Это предполагает, что для повышения уровня требовалось ровно exp_to_level опыта.
        # 2. Вычитаем это количество из current_exp.
        # 3. (Опционально) Увеличиваем требование exp_to_level для следующего уровня.
        
        # Пример логики с фиксированным ростом:
        exp_cost_for_previous_level = self.exp_to_level
        self.current_exp -= exp_cost_for_previous_level
        self.current_exp = max(0, self.current_exp) 
        
        self.exp_to_level = int(self.exp_to_level * 1.5) # Увеличиваем на 50%

    # --- Методы управления опытом ---
    
    def add_experience(self, amount: int) -> None:
        """Добавляет опыт персонажу и публикует событие.
        
        Args:
            amount: Количество опыта для добавления. Должно быть неотрицательным.
        """
        if amount <= 0:
            return # Нет смысла добавлять ноль или отрицательный опыт
            
        self.current_exp += amount
        self._publish_experience_gained()

    def _publish_experience_gained(self) -> None:
        """Создает и публикует событие получения опыта."""
        # Проверяем наличие context и event_bus через context
        if self.context and hasattr(self.context, 'event_bus') and self.context.event_bus:
            event = ExperienceGainedEvent(
                source=self,
                exp_to_level=self.exp_to_level,
                current_exp=self.current_exp
            )
            self._publish(event) # Используем метод из PublisherPropertyMixin

    def get_progress_to_next_level(self) -> float:
        """Получает прогресс до следующего уровня в виде доли (0.0 - 1.0)."""
        if self.exp_to_level <= 0:
            return 0.0 # Избегаем деления на ноль
        return min(1.0, self.current_exp / self.exp_to_level)

    def __str__(self) -> str:
        """Строковое представление опыта."""
        return (f"Experience(current={self.current_exp}, "
                f"to_level={self.exp_to_level}, "
                f"progress={self.get_progress_to_next_level():.2%})")


# ==================== Обработчики событий наград ====================

def handle_experience_gained(event: RewardExperienceGainedEvent) -> None:
    """
    Обработчик события получения опыта персонажем как награды.
    
    Этот обработчик подписывается на событие ExperienceGainedEvent из модуля наград
    (game.events.reward_events) и вызывает метод add_experience у свойства
    опыта персонажа, чтобы фактически увеличить его опыт.
    
    Args:
        event (RewardExperienceGainedEvent): Событие получения опыта как награды.
    """
    character = event.character
    amount = event.amount
    
    # Проверка: у персонажа должно быть свойство опыта
    if not hasattr(character, 'experience') or character.experience is None:
        # Можно залогировать ошибку или предупреждение
        print(f"Предупреждение: Персонаж {character.name} не имеет свойства опыта для получения {amount} XP.")
        return

    # Вызываем метод add_experience, который добавит опыт и опубликует
    # внутреннее событие ExperienceGainedEvent (из game.events.character)
    try:
        character.experience.add_experience(amount)
        # print(f"{character.name} получил {amount} опыта как награду. Текущий опыт: {character.experience.current_exp}") # Для отладки
    except Exception as e:
        print(f"Ошибка при добавлении {amount} XP персонажу {character.name}: {e}")

# Функция для регистрации обработчика (вызывается при инициализации игры)
def register_experience_handlers(context: 'GameContext') -> None:
    """
    Регистрирует обработчики событий, связанных с опытом, в шине событий.
    
    Args:
        context (GameContext): Игровой контекст, содержащий EventBus.
    """
    # Подписываемся на ExperienceGainedEvent ИЗ СИСТЕМЫ НАГРАД.
    # Источник=None означает, что мы слушаем это событие от любого источника.
    # Приоритет NORMAL (10), так как это стандартная обработка наград.
    context.event_bus.subscribe(
        source=None, # Слушаем от всех
        event_type=RewardExperienceGainedEvent, # Важно: именно из reward_events
        callback=handle_experience_gained,
        priority=10 # NORMAL_PRIORITY из event_bus.py
    )
