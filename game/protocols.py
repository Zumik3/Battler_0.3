# game/protocols.py
"""Протоколы (интерфейсы) для взаимодействия компонентов игры."""

from typing import Protocol, List, Dict, Any, Optional, TYPE_CHECKING, Callable

# Используем TYPE_CHECKING, чтобы избежать циклических импортов в аннотациях
if TYPE_CHECKING:
    from game.entities.character import Character

# --- Протоколы для подсистем ---

class Ability(Protocol):
    """Протокол для способности."""
    name: str
    description: str
    energy_cost: int
    # Можно добавить другие общие атрибуты
    
    def can_use(self, user: 'Character') -> bool: ...
    def use(self, user: 'Character', targets: List['Character'], **kwargs) -> Any: ...

class StatusEffect(Protocol):
    """Протокол для статус-эффекта."""
    name: str
    description: str
    duration: int # Оставшаяся продолжительность
    
    def apply(self, target: 'Character') -> Dict[str, Any]: # Возвращает словарь с сообщением или результатом
        """Применить эффект к цели."""
        ...
    def update(self, target: 'Character') -> Dict[str, Any]: # Возвращает словарь с сообщением или результатом
        """Обновить эффект (например, нанести урон от отравления)."""
        ...
    def remove(self, target: 'Character') -> Dict[str, Any]: # Возвращает словарь с сообщением или результатом
        """Удалить эффект с цели."""
        ...
    def is_expired(self) -> bool: ...

class Stats(Protocol):
    """Протокол для базовых характеристик."""
    strength: int
    agility: int
    intelligence: int
    vitality: int
    # ... другие базовые характеристики

class Attributes(Protocol): # <-- ИЗМЕНЕНО: DerivedStats -> Attributes
    """Протокол для атрибутов персонажа."""
    max_hp: int
    max_energy: int
    attack_power: int
    defense: int
    # ... другие атрибуты

# --- Протоколы для менеджеров ---

class AbilityManagerProtocol(Protocol):
    """Протокол для менеджера способностей."""
    def add_ability(self, name: str, ability: Ability) -> None: ...
    def get_available_abilities(self, character: 'Character') -> List[str]: ...
    def use_ability(self, name: str, user: 'Character', targets: List['Character'], **kwargs) -> Any: ...
    def update_cooldowns(self) -> None: ...

class StatusEffectManagerProtocol(Protocol):
    """Протокол для менеджера статус-эффектов."""
    def add_effect(self, effect: StatusEffect) -> Dict[str, Any]: ...
    def remove_effect(self, effect_name: str) -> bool: ...
    def update_effects(self) -> List[Dict[str, Any]]: # Возвращает список сообщений/результатов
        """Обновить все эффекты и вернуть список результатов."""
        ...
    def has_effect(self, effect_name: str) -> bool: ...
    def get_all_effects(self) -> List[StatusEffect]: ...
    def clear_all_effects(self) -> List[Dict[str, Any]]: # Возвращает список сообщений/результатов
        """Очистить все эффекты и вернуть список результатов."""
        ...

# --- Протоколы для системы уровней/опыта ---
# Эти протоколы позволят нам в будущем легко подменить систему роста

class ExperienceCalculatorProtocol(Protocol):
    """Протокол для калькулятора опыта."""
    def calculate_exp_for_next_level(self, current_level: int) -> int: ...
    def calculate_stat_increase(self, base_stat: int, growth_rate: float, level: int) -> int: ...

class LevelUpHandlerProtocol(Protocol):
    """Протокол для обработчика повышения уровня."""
    def handle_level_up(self, character: 'Character') -> List[Dict[str, Any]]:
        """Обработать повышение уровня и вернуть список результатов."""
        ...
