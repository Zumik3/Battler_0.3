# game/protocols.py
"""Протоколы, определяющие интерфейсы для различных компонентов игры."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Protocol, Optional, TYPE_CHECKING, runtime_checkable

if TYPE_CHECKING:
    from game.entities.character import Character as CharacterType
    from game.results import ActionResult, ExperienceGainedResult
    from game.config import GameConfig
    from game.systems.event_bus import IEventBus

# ==================== Базовые протоколы данных ====================

class StatsProtocol(Protocol):
    """Протокол для базовых характеристик персонажа."""
    strength: int
    agility: int
    intelligence: int
    vitality: int


@runtime_checkable
class StatsConfigurable(Protocol):
    """Протокол для объектов, предоставляющих конфигурацию характеристик."""
    def calculate_all_stats_at_level(self, level: int) -> Dict[str, int]: ...

    def get_base_stats(self) -> Dict[str, int]: ...

    def get_growth_rates(self) -> Dict[str, int]: ...


class Attributes(Protocol):
    """Протокол для производных атрибутов персонажа."""
    max_hp: int
    max_energy: int
    attack_power: int
    defense: int

    def recalculate(self, stats: StatsProtocol, config: 'GameConfig') -> None:
        """Пересчитать атрибуты на основе базовых характеристик."""
        ...


class HealthPropertyProtocol(Protocol):
    """Протокол для производных атрибутов персонажа."""
    max_health: int
    health: int


class EnergyPropertyProtocol(Protocol):
    """Протокол для производных атрибутов персонажа."""
    max_energy: int
    energy: int


class CombatPropertyProtocol(Protocol):
    """Протокол для производных атрибутов персонажа."""
    attack_power: int
    defence: int


class ExperiencePropertyProtocol(Protocol):
    """Протокол для производных атрибутов персонажа."""
    def add_experience(self, amount: int) -> None:
        """Добавляет опыт персонажу."""
        ...


class LevelPropertyProtocol(Protocol):
    """Протокол для производных атрибутов персонажа."""
    def level_up(self) -> None:
        """Добавляет уровень персонажу."""
        ...


# ==================== Протоколы игровых систем ====================

class AbilityManagerProtocol(Protocol):
    """Протокол для менеджера способностей."""
    def add_ability(self, ability: 'Ability') -> List['ActionResult']:
        """Добавляет способность персонажу."""
        ...

    def use_ability(self, ability_name: str, target: List['CharacterType'], **kwargs) -> List['ActionResult']:
        """Использовать способность на цель."""
        ...

    def get_available_abilities(self) -> List['Ability']:
        """Получить список доступных способностей."""
        ...

    def update_cooldowns(self) -> List['ActionResult']:
        """Обновить кулдауны способностей."""
        ...

class StatusEffectManagerProtocol(Protocol):
    """Протокол для менеджера статус-эффектов."""
    def apply_effect(self, effect: 'StatusEffect') -> List['ActionResult']:
        """Применить эффект к персонажу."""
        ...

    def remove_effect(self, effect_name: str) -> List['ActionResult']:
        """Удалить эффект по имени."""
        ...

    def update_effects(self) -> List['ActionResult']:
        """Обновить эффекты."""
        ...

    def get_effect(self, effect_name: str) -> Optional['StatusEffect']:
        """Получить эффект по имени."""
        ...

    def get_all_effects(self) -> List['StatusEffect']:
        """Получить список всех активных эффектов."""
        ...

    def clear_all_effects(self) -> List['ActionResult']:
        """Очистить все эффекты и вернуть список результатов."""
        ...

# ==================== Протоколы систем опыта и уровней ====================

class ExperienceCalculatorProtocol(Protocol):
    def calculate_exp_for_next_level(self, current_level: int) -> int:
        """Рассчитывает опыт, необходимый для следующего уровня."""
        ...

class LevelUpHandlerProtocol(Protocol):
    def handle_level_up(self, character: 'CharacterType') -> List['ActionResult']:
        """Обрабатывает повышение уровня и возвращает результаты."""
        ...

class ExperienceSystemProtocol(Protocol):
    def add_experience(self, amount: int) -> None:
        """Добавляет опыт персонажу и возвращает результаты."""
        ...

class LevelingSystemProtocol(Protocol):
    def try_level_up(self, character: 'CharacterType') -> List['ActionResult']:
        """Проверяет и выполняет повышение уровня, если возможно."""
        ...

# ==================== Протоколы генераторов ====================

class MonsterNamerProtocol(Protocol):
    """Протокол для генератора имен монстров."""
    
    def generate_name(self, monster_role: str) -> str:
        """
        Генерирует имя для монстра на основе его роли.

        Args:
            monster_role: Роль/тип монстра (например, 'goblin', 'dragon').

        Returns:
            Сгенерированное имя.
        """
        ...

# ==================== Базовые абстрактные классы ====================

class Character(ABC):
    """Абстрактный базовый класс, представляющий персонажа в игре."""
    pass

class Ability(ABC):
    """Абстрактный базовый класс для способностей."""
    def __init__(self, name: str, energy_cost: int, description: str = ""):
        self.name = name
        self.energy_cost = energy_cost
        self.description = description

    @abstractmethod
    def activate(self, caster: 'CharacterType', target: 'CharacterType') -> List['ActionResult']:
        """Активировать способность."""
        ...

class StatusEffect(ABC):
    """Абстрактный базовый класс для статус-эффектов."""
    def __init__(self, name: str, duration: int, description: str = ""):
        self.name = name
        self.duration = duration
        self.description = description

    @abstractmethod
    def apply(self, target: 'CharacterType') -> List['ActionResult']:
        """Применить эффект к цели."""
        ...

    @abstractmethod
    def remove(self, target: 'CharacterType') -> List['ActionResult']:
        """Удалить эффект с цели."""
        ...

    def tick(self, target: 'CharacterType') -> List['ActionResult']:
        """Выполнить действие эффекта за ход (если применимо)."""
        self.duration -= 1
        if self.duration <= 0:
            # Сигнализируем, что эффект нужно удалить
            return [ActionResult(type="effect_expired", message=f"Эффект {self.name} истек")]
        return []

    @property
    def is_expired(self) -> bool:
        """Проверить, истек ли эффект."""
        return self.duration <= 0


class CharacterAttributesConfig(Protocol):
    """Протокол для части конфигурации, связанной с расчетом атрибутов."""
    # Предполагаем, что config.character имеет эти атрибуты
    hp_per_vitality: int
    energy_per_intelligence: int
    attack_per_strength: int
    defense_per_agility: float


class PropertyContext(Protocol):
    """Интерфейс для контекста, предоставляемого свойству."""
    
    @property
    def event_bus(self) -> 'IEventBus':
        """Получить доступ к шине событий."""
        ...
        
    def get_service(self, service_name: str) -> Any:
        """Получить доступ к произвольному сервису по имени.
        
        Например:
        - logger = context.get_service('logger')
        - game_config = context.get_service('game_config')
        - entity_manager = context.get_service('entity_manager')
        """
        ...
        
    def trigger_action(self, action_type: str, data: Any) -> None:
        """Инициировать какое-либо действие в системе.
        
        Например:
        - context.trigger_action('log', {'message': '...', 'level': 'debug'})
        - context.trigger_action('spawn_effect', {...})
        """
        ...
        
    # Можно добавить другие общие методы, например:
    # def get_owner(self) -> Any: ...
    # def get_property(self, prop_type: type) -> Any: ...
