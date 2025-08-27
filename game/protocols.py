# game/protocols.py
"""Протоколы, определяющие интерфейсы для различных компонентов игры."""

from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Any, Protocol, Optional, TYPE_CHECKING, runtime_checkable



if TYPE_CHECKING:
    from game.entities.character import Character as CharacterType
    from game.config import GameConfig
    from game.systems.events.bus import IEventBus
    from game.actions.action import Action

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
    """Протокол для свойства, управляющего здоровьем персонажа."""
    max_health: int
    health: int


class EnergyPropertyProtocol(Protocol):
    """Протокол для свойства, управляющего энергией персонажа."""
    max_energy: int
    energy: int


class CombatPropertyProtocol(Protocol):
    """Протокол для свойства, управляющего боевыми показателями персонажа."""
    attack_power: int
    defense: int


class ExperiencePropertyProtocol(Protocol):
    """Протокол для свойства, управляющего опытом персонажа."""
    def add_experience(self, amount: int) -> None:
        """Добавляет опыт персонажу."""
        ...


class LevelPropertyProtocol(Protocol):
    """Протокол для свойства, управляющего уровнем персонажа."""
    def level_up(self, amount: int = 1) -> None:
        """Добавляет уровень персонажу."""
        ...


# ==================== Протоколы игровых систем ====================

class AbilityRegistryProtocol(Protocol):
    
    def is_registered(self, ability_name: str) -> bool:
        """Проверяет, зарегистрирована ли способность с указанным именем.
        
        Args:
            ability_name: Имя способности для проверки.
            
        Returns:
            True, если способность зарегистрирована, иначе False.
        """
        ...

    def get_factory(self, ability_name: str) -> Callable[['CharacterType'], 'Action']:
        ...

class AbilityManagerProtocol(Protocol):
    """Протокол для менеджера способностей."""
    def add_ability(self, ability_name: str) -> None:
        """Добавляет способность персонажу по имени."""
        ...

    def use_ability(self, ability_name: str, targets: List['CharacterType'], **kwargs) -> None:
        """Использовать способность на цель."""
        ...

    def get_available_abilities(self) -> List[str]:
        """Получить список доступных способностей."""
        ...


# ==================== Протоколы систем опыта и уровней ====================

class ExperienceCalculatorProtocol(Protocol):
    def calculate_exp_for_next_level(self, current_level: int) -> int:
        """Рассчитывает опыт, необходимый для следующего уровня."""
        ...


class LevelUpHandlerProtocol(Protocol):
    def handle_level_up(self, character: 'CharacterType') -> None:
        """Обрабатывает повышение уровня и возвращает результаты."""
        ...


class ExperienceSystemProtocol(Protocol):
    def add_experience(self, amount: int) -> None:
        """Добавляет опыт персонажу и возвращает результаты."""
        ...


class LevelingSystemProtocol(Protocol):
    def try_level_up(self, character: 'CharacterType') -> None:
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


class CharacterAttributesConfig(Protocol):
    """Протокол для части конфигурации, связанной с расчетом атрибутов."""
    # Предполагаем, что config.character имеет эти атрибуты
    hp_per_vitality: int
    energy_per_intelligence: int
    attack_per_strength: int
    defense_per_agility: float


class PropertyContextProtocol(Protocol):
    """Интерфейс для контекста, предоставляемого свойству."""
    
    _character: 'CharacterType'

    @property
    def event_bus(self) -> 'IEventBus':
        """Получить доступ к шине событий."""
        ...

    @property
    def character(self) -> 'CharacterType':
        """Получить доступ к персонажу-владельцу."""
        ...
