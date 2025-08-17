# game/protocols.py
"""Протоколы, определяющие интерфейсы для различных компонентов игры."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Protocol, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.entities.character import Character as CharacterType
    from game.results import ActionResult, ExperienceGainedResult
    from game.config import GameConfig

# ==================== Базовые протоколы данных ====================

class Stats(Protocol):
    """Протокол для базовых характеристик персонажа."""
    strength: int
    agility: int
    intelligence: int
    vitality: int

class Attributes(Protocol):
    """Протокол для производных атрибутов персонажа."""
    max_hp: int
    max_energy: int
    attack_power: int
    defense: int

    def recalculate(self, stats: Stats, config: 'GameConfig') -> None:
        """Пересчитать атрибуты на основе базовых характеристик."""
        ...

# ==================== Протоколы игровых систем ====================

class AbilityManagerProtocol(Protocol):
    """Протокол для менеджера способностей."""
    def add_ability(self, ability: 'Ability') -> List[ActionResult]:
        """Добавляет способность персонажу."""
        ...

    def use_ability(self, ability_name: str, target: List['CharacterType'], **kwargs) -> List[ActionResult]:
        """Использовать способность на цель."""
        ...

    def get_available_abilities(self) -> List['Ability']:
        """Получить список доступных способностей."""
        ...

    def update_cooldowns(self) -> List[ActionResult]:
        """Получить список доступных способностей."""
        ...

class StatusEffectManagerProtocol(Protocol):
    """Протокол для менеджера статус-эффектов."""
    def apply_effect(self, effect: 'StatusEffect') -> List[ActionResult]:
        """Применить эффект к персонажу."""
        ...

    def remove_effect(self, effect_name: str) -> List[ActionResult]:
        """Удалить эффект по имени."""
        ...

    def update_effects(self) -> List[ActionResult]:
        """Обновить эффекты."""
        ...

    def get_effect(self, effect_name: str) -> Optional['StatusEffect']:
        """Получить эффект по имени."""
        ...

    def get_all_effects(self) -> List['StatusEffect']:
        """Получить список всех активных эффектов."""
        ...

    def clear_all_effects(self) -> List[ActionResult]:
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
    def add_experience(self, character: 'CharacterType', amount: int) -> List['ExperienceGainedResult']:
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
    # (Определение класса находится в game/entities/character.py)
    pass

class Ability(ABC):
    """Абстрактный базовый класс для способностей."""
    def __init__(self, name: str, energy_cost: int, description: str = ""):
        self.name = name
        self.energy_cost = energy_cost
        self.description = description

    @abstractmethod
    def activate(self, caster: 'CharacterType', target: 'CharacterType') -> List[Dict[str, Any]]:
        """Активировать способность."""
        ...

class StatusEffect(ABC):
    """Абстрактный базовый класс для статус-эффектов."""
    def __init__(self, name: str, duration: int, description: str = ""):
        self.name = name
        self.duration = duration
        self.description = description

    @abstractmethod
    def apply(self, target: 'CharacterType') -> List[Dict[str, Any]]:
        """Применить эффект к цели."""
        ...

    @abstractmethod
    def remove(self, target: 'CharacterType') -> List[Dict[str, Any]]:
        """Удалить эффект с цели."""
        ...

    def tick(self, target: 'CharacterType') -> List[Dict[str, Any]]:
        """Выполнить действие эффекта за ход (если применимо)."""
        # По умолчанию эффект просто уменьшает свою длительность
        self.duration -= 1
        if self.duration <= 0:
            return target.status_manager.remove_effect(self.name) # type: ignore
        return []