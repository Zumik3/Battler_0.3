# game/protocols.py
"""Протоколы, определяющие интерфейсы для различных компонентов игры."""

import traceback
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Protocol, Optional

# Импорты с TYPE_CHECKING для избежания циклических импортов
# в аннотациях типов на уровне модуля
# (импортируем только при аннотации типов, а не во время выполнения)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.entities.character import Character as CharacterType


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

    def recalculate(self, stats: Stats) -> None:
        """Пересчитать атрибуты на основе базовых характеристик."""
        ...


class AbilityManagerProtocol(Protocol):
    """Протокол для менеджера способностей."""
    def use_ability(self, ability_name: str, target: 'CharacterType') -> List[Dict[str, Any]]:
        """Использовать способность на цель."""
        ...

    def get_available_abilities(self) -> List[str]:
        """Получить список доступных способностей."""
        ...


class StatusEffectManagerProtocol(Protocol):
    """Протокол для менеджера статус-эффектов."""
    def apply_effect(self, effect: 'StatusEffect') -> List[Dict[str, Any]]:
        """Применить эффект к персонажу."""
        ...

    def remove_effect(self, effect_name: str) -> List[Dict[str, Any]]:
        """Удалить эффект по имени."""
        ...

    def get_effect(self, effect_name: str) -> Optional['StatusEffect']:
        """Получить эффект по имени."""
        ...

    def get_all_effects(self) -> List['StatusEffect']:
        """Получить список всех активных эффектов."""
        ...

    def clear_all_effects(self) -> List[Dict[str, Any]]:
        """Очистить все эффекты и вернуть список результатов."""
        ...


# Протоколы для системы уровней/опыта
# Эти протоколы позволят нам в будущем легко подменить систему роста
class ExperienceCalculatorProtocol(Protocol):
    """Протокол для калькулятора опыта."""
    def calculate_exp_for_next_level(self, current_level: int) -> int:
        """Рассчитать опыт, необходимый для следующего уровня."""
        ...

    def calculate_stat_increase(self, base_stat: int, growth_rate: float, level: int) -> int:
        """Рассчитать увеличение характеристики."""
        ...


class LevelUpHandlerProtocol(Protocol):
    """Протокол для обработчика повышения уровня."""
    def handle_level_up(self, character: 'CharacterType') -> List[Dict[str, Any]]:
        """Обработать повышение уровня и вернуть список результатов."""
        ...


# Базовые абстрактные классы
class Character(ABC):
    """Абстрактный базовый класс, представляющий персонажа в игре."""
    # (Определение класса находится в game/entities/character.py)
    pass # fallback если абстрактные методы не реализованы корректно


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

# --- Протокол для генератора имен монстров ---
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
        ... # Тело метода в протоколе пустое, описывает интерфейс
