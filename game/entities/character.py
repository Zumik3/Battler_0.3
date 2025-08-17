# game/entities/character.py
"""Базовый класс персонажа в игре."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING
from game.protocols import (
    Stats, 
    Attributes,
    AbilityManagerProtocol, 
    StatusEffectManagerProtocol,
    Ability,
    StatusEffect
)
from game.config import get_config
from game.results import ActionResult

if TYPE_CHECKING:
    from game.entities.character import Character as CharacterType

# ==================== Вспомогательные классы ====================

@dataclass
class CharacterConfig:
    """Конфигурация для создания персонажа."""
    
    # Базовые параметры
    name: str
    role: str
   
    # Параметры для системы уровней/характеристик
    base_stats: Dict[str, int]
    growth_rates: Dict[str, float]
    level: int = 1
    is_player: bool = field(default=False)

    class_icon: str = "?"
    class_icon_color: str = ""
    description: str = ""
    starting_abilities: List[str] = field(default_factory=list)

    # Внедрение зависимостей через конструктор
    stats_factory: Optional[Callable[[str, int, Dict[str, int], Dict[str, float]], 'Stats']] = None
    attributes_factory: Optional[Callable[['Stats', Any], 'Attributes']] = None
    ability_manager_factory: Optional[Callable[['CharacterType'], 'AbilityManagerProtocol']] = None
    status_effect_manager_factory: Optional[Callable[['CharacterType'], 'StatusEffectManagerProtocol']] = None

@dataclass
class SimpleStats:
    strength: int = 0
    agility: int = 0
    intelligence: int = 0
    vitality: int = 0


# class SimpleStats:
#     """Простая реализация базовых характеристик."""
#     def __init__(self):
#         self.strength = 0
#         self.agility = 0
#         self.intelligence = 0
#         self.vitality = 0


@dataclass
class SimpleAttributes:
    max_hp: int = 0
    max_energy: int = 0
    attack_power: int = 0
    defense: int = 0

    def recalculate(self, stats: Stats, config: Any) -> None:
        """Пересчитывает атрибуты на основе новых характеристик."""
        self.max_hp = config.character.base_max_hp + (stats.vitality * config.character.hp_per_vitality)
        self.max_energy = config.character.base_max_energy + (stats.intelligence * config.character.energy_per_intelligence)
        self.attack_power = stats.strength * config.character.attack_per_strength
        self.defense = int(stats.agility * config.character.defense_per_agility)


# class SimpleAttributes:
#     """Простая реализация производных атрибутов."""
#     def __init__(self, character: 'CharacterType', stats: Stats):
#         self.character = character
#         self.stats = stats
#         config = get_config() # Получаем конфигурацию
        
#         # Расчет производных атрибутов с использованием настроек
#         self.max_hp = config.character.base_max_hp + (stats.vitality * config.character.hp_per_vitality)
#         self.max_energy = config.character.base_max_energy + (stats.intelligence * config.character.energy_per_intelligence)
#         self.attack_power = stats.strength * config.character.attack_per_strength
#         self.defense = int(stats.agility * config.character.defense_per_agility)

#     def recalculate(self, stats: Stats) -> None:
#         """
#         Пересчитать атрибуты на основе новых базовых характеристик.
#         Это реализация метода, требуемого протоколом Attributes.
#         """
#         config = get_config()
#         # Повторяем логику расчета из __init__
#         self.max_hp = config.character.base_max_hp + (stats.vitality * config.character.hp_per_vitality)
#         self.max_energy = config.character.base_max_energy + (stats.intelligence * config.character.energy_per_intelligence)
#         self.attack_power = stats.strength * config.character.attack_per_strength
#         self.defense = int(stats.agility * config.character.defense_per_agility)
#         # Обновляем ссылку на stats
#         self.stats = stats

# --- Основной класс персонажа ---
class Character(ABC):
    """Абстрактный базовый класс, представляющий персонажа в игре."""

    def __init__(self, config: CharacterConfig):
        
        self.alive = True
        
        self.name = config.name
        self.role = config.role
        self.level = config.level
        self.is_player = config.is_player

        self.class_icon = config.class_icon
        self.class_icon_color = config.class_icon_color

        self.base_stats_dict = config.base_stats
        self.growth_rates_dict = config.growth_rates

         # Используем фабрики из конфига или по умолчанию
        self._stats_factory = config.stats_factory or (lambda role, level, base, growth: Character.default_stats_factory(role, level, base, growth))
        self._attributes_factory = config.attributes_factory or (lambda stats, config_obj: Character.default_attributes_factory(stats, config_obj))

        # Инициализация характеристик
        self.stats: Stats = self._stats_factory(self.role, self.level, self.base_stats_dict, self.growth_rates_dict)
        self.attributes: Attributes = self._attributes_factory(self.stats, get_config())


        # Инициализируем hp и энергию
        self.hp = self.attributes.max_hp
        self.energy = self.attributes.max_energy

        # Менеджеры (внедрение зависимостей)
        self._ability_manager: Optional[AbilityManagerProtocol] = None
        if config.ability_manager_factory:
            self._ability_manager = config.ability_manager_factory(self)

        self._status_manager: Optional[StatusEffectManagerProtocol] = None
        if config.status_effect_manager_factory:
            self._status_manager = config.status_effect_manager_factory(self)

    # ==================== Вспомогательные методы для фабрик (по умолчанию) ====================
    # Вспомогательные фабрики (можно разместить внутри класса или отдельно)
    @staticmethod
    def default_stats_factory(role: str, level: int, base_stats_dict: Dict[str, int], growth_rates_dict: Dict[str, float]) -> Stats:
        """Фабрика по умолчанию для создания Stats."""
        
        level_multiplier = level * 0.1
        return SimpleStats(
            strength=int(base_stats_dict.get('strength', 10) * (1 + level_multiplier * growth_rates_dict.get('strength', 1.0))),
            agility=int(base_stats_dict.get('agility', 10) * (1 + level_multiplier * growth_rates_dict.get('agility', 1.0))),
            intelligence=int(base_stats_dict.get('intelligence', 10) * (1 + level_multiplier * growth_rates_dict.get('intelligence', 1.0))),
            vitality=int(base_stats_dict.get('vitality', 10) * (1 + level_multiplier * growth_rates_dict.get('vitality', 1.0))),
        )

    @staticmethod
    def default_attributes_factory(stats: Stats, config: Any) -> Attributes:
        """Фабрика по умолчанию для создания Attributes."""
        
        attr = SimpleAttributes()
        attr.recalculate(stats, config)
        return attr

    def _update_attributes(self) -> None:
        """Обновляет атрибуты на основе текущих характеристик."""
        config = get_config()
        self.attributes.recalculate(self.stats, config)
        # Обновляем hp и энергию до максимума при пересчете
        self.hp = self.attributes.max_hp
        self.energy = self.attributes.max_energy

    def level_up(self) -> List[ActionResult]:
        """
        Повышает уровень персонажа.
        Возвращает список сообщений/результатов.
        """
        self.level += 1
        
        # Пересчитываем характеристики
        self.stats = self._stats_factory(self.role, self.level, self.base_stats_dict, self.growth_rates_dict)
        
        # Пересчитываем атрибуты
        self._update_attributes()
        
        # Возвращаем результат как ActionResult
        return [ActionResult(
            type="level_up",
            message=f"{self.name} достиг уровня {self.level}!"
        )]

    # ==================== Свойства ====================
    @property
    def ability_manager(self) -> Optional[AbilityManagerProtocol]:
        """Получение менеджера способностей."""
        return self._ability_manager

    @property
    def status_manager(self) -> Optional[StatusEffectManagerProtocol]:
        """Получение менеджера статус-эффектов."""
        return self._status_manager

    # ==================== Основные методы персонажа ====================
    def is_alive(self) -> bool:
        """Проверяет, жив ли персонаж."""
        return self.alive

    def get_level(self) -> int:
        """Возвращает уровень персонажа."""
        return self.level

    def on_death(self) -> List[Dict[str, Any]]:
        """
        Вызывается при смерти персонажа. 
        Возвращает список сообщений/результатов.
        """
        results = []

        # Очищаем все активные статус-эффекты
        if self._status_manager is not None:
            clear_results = self._status_manager.clear_all_effects()
            results.extend(clear_results)

        # Добавляем сообщение о смерти
        results.append({"type": "death", "message": f"{self.name} погибает!"})
        return results

    # ==================== Боевые методы ====================
    def take_damage(self, damage: int) -> List[Dict[str, Any]]:
        """
        Наносит урон персонажу, учитывая защиту.
        Возвращает список сообщений/результатов.
        """
        results = []
        # Учитываем защиту из attributes.defense
        actual_damage = max(0, damage - self.attributes.defense // 2)  # Может быть 0 урон
        actual_damage = max(1, actual_damage) if damage > 0 else 0  # Минимум 1 урон если был урон

        self.hp -= actual_damage
        results.append({
            "type": "damage_taken", 
            "target": self.name, 
            "damage": actual_damage,
            "hp_left": self.hp
        })

        if self.hp <= 0:
            self.hp = 0
            if self.alive:  # Проверяем, чтобы не вызывать on_death дважды
                self.alive = False
                death_results = self.on_death()
                results.extend(death_results)

        return results

    def take_heal(self, heal_amount: int) -> List[Dict[str, Any]]:
        """
        Исцеляет персонажа и возвращает список сообщений/результатов.
        """
        results = []
        old_hp = self.hp
        self.hp = min(self.attributes.max_hp, self.hp + heal_amount)
        actual_heal = self.hp - old_hp
        results.append({
            "type": "healed", 
            "target": self.name, 
            "heal_amount": actual_heal,
            "hp_now": self.hp
        })
        return results

    # ==================== Энергия ====================
    def restore_energy(self, amount: Optional[int] = None, percentage: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Восстанавливает энергию персонажа.
        :param amount: конкретное количество энергии для восстановления
        :param percentage: процент от максимальной энергии для восстановления
        Возвращает список сообщений/результатов.
        """
        results = []
        old_energy = self.energy

        if percentage is not None:
            restore_amount = int(self.attributes.max_energy * (percentage / 100.0))
            self.energy = min(self.attributes.max_energy, self.energy + restore_amount)
        elif amount is not None:
            self.energy = min(self.attributes.max_energy, self.energy + amount)
        else:
            self.energy = self.attributes.max_energy  # Полное восстановление

        actual_restore = self.energy - old_energy
        if actual_restore > 0:
            results.append({
                "type": "energy_restored", 
                "target": self.name, 
                "amount": actual_restore,
                "energy_now": self.energy
            })

        return results

    def spend_energy(self, amount: int) -> bool:
        """
        Тратит энергию персонажа.
        Возвращает True, если энергия была потрачена, иначе False.
        """
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False

    # ==================== Способности ====================
    def add_ability(self, name: str, ability: Ability) -> None:
        """Добавляет способность персонажу."""
        if self._ability_manager:
            self._ability_manager.add_ability(name, ability)

    def get_available_abilities(self) -> List[str]:
        """Получает список доступных способностей."""
        if self._ability_manager:
            return self._ability_manager.get_available_abilities(self)
        return []

    def use_ability(self, name: str, targets: List['CharacterType'], **kwargs) -> List[Dict[str, Any]]:
        """
        Использует способность по имени.
        Возвращает список сообщений/результатов от способности и менеджера.
        """
        results = []
        if self._ability_manager:
            ability_result = self._ability_manager.use_ability(name, self, targets, **kwargs)
            if ability_result:
                if isinstance(ability_result, list):
                    results.extend(ability_result)
                else:
                    results.append(ability_result)
        return results

    def update_ability_cooldowns(self) -> None:
        """Обновляет кулдауны способностей в конце раунда."""
        if self._ability_manager:
            self._ability_manager.update_cooldowns()

    # ==================== Статус-эффекты ====================
    def add_status_effect(self, effect: StatusEffect) -> List[Dict[str, Any]]:
        """Добавляет статус-эффект персонажу. Возвращает результат от менеджера."""
        if self._status_manager:
            return [self._status_manager.add_effect(effect)]
        return []

    def remove_status_effect(self, effect_name: str) -> List[Dict[str, Any]]:
        """Удаляет статус-эффект по имени. Возвращает результат."""
        results = []
        if self._status_manager:
            success = self._status_manager.remove_effect(effect_name)
            if success:
                results.append({"type": "effect_removed", "effect": effect_name, "target": self.name})
            else:
                results.append({"type": "error", "message": f"Эффект {effect_name} не найден у {self.name}"})
        return results

    def update_status_effects(self) -> List[Dict[str, Any]]:
        """Обновляет все активные статус-эффекты. Возвращает список результатов."""
        if self._status_manager:
            return self._status_manager.update_effects()
        return []

    def has_status_effect(self, effect_name: str) -> bool:
        """Проверяет, есть ли у персонажа определенный статус-эффект."""
        if self._status_manager:
            return self._status_manager.has_effect(effect_name)
        return False

    def get_active_status_effects(self) -> List[StatusEffect]:
        """Возвращает список всех активных статус-эффектов."""
        if self._status_manager:
            return self._status_manager.get_all_effects()
        return []
