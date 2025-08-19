# game/entities/character.py
"""Базовый класс персонажа в игре."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING
from game.entities.properties.health import HealthProperty
from game.entities.properties.energy import EnergyProperty
from game.protocols import (
    Stats, 
    Attributes,
    AbilityManagerProtocol, 
    StatusEffectManagerProtocol,
    Ability,
    StatusEffect
)
from game.config import GameConfig, get_config
from game.results import (
    ActionResult, 
    DamageTakenResult, 
    HealedResult
)


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
    ability_manager_factory: Optional[Callable[['Character'], 'AbilityManagerProtocol']] = None
    status_effect_manager_factory: Optional[Callable[['Character'], 'StatusEffectManagerProtocol']] = None

@dataclass
class SimpleStats:
    strength: int = 0
    agility: int = 0
    intelligence: int = 0
    vitality: int = 0

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

# ==================== Основной класс персонажа ====================
class Character(ABC):
    """Абстрактный базовый класс, представляющий персонажа в игре."""

    def __init__(self, character_config: CharacterConfig, game_config: 'GameConfig'):

        self.game_config = game_config

        self.alive = True
        self.name = character_config.name
        self.role = character_config.role
        self.level = character_config.level
        self.is_player = character_config.is_player

        self.class_icon = character_config.class_icon
        self.class_icon_color = character_config.class_icon_color

        self.base_stats_dict = character_config.base_stats
        self.growth_rates_dict = character_config.growth_rates

        # Используем фабрики из конфига или по умолчанию
        self._stats_factory = character_config.stats_factory or (lambda role, level, base, growth: Character.default_stats_factory(role, level, base, growth))
        self._attributes_factory = character_config.attributes_factory or (lambda stats, config_obj: Character.default_attributes_factory(stats, config_obj))

        # Инициализация характеристик
        self.stats: Stats = self._stats_factory(self.role, self.level, self.base_stats_dict, self.growth_rates_dict)
        self.attributes: Attributes = self._attributes_factory(self.stats, game_config)

        # Инициализируем hp и энергию
        self.health = HealthProperty(self.attributes.max_hp, 0)
        self.energy = EnergyProperty(self.attributes.max_energy, 0)

        # Менеджеры (внедрение зависимостей)
        self._ability_manager: Optional[AbilityManagerProtocol] = None
        if character_config.ability_manager_factory:
            self._ability_manager = character_config.ability_manager_factory(self)

        self._status_manager: Optional[StatusEffectManagerProtocol] = None
        if character_config.status_effect_manager_factory:
            self._status_manager = character_config.status_effect_manager_factory(self)

    # ==================== Фабричные методы ====================
    @staticmethod
    def default_stats_factory(
        role: str, 
        level: int, 
        base_stats_dict: Dict[str, int], 
        growth_rates_dict: Dict[str, float]
        ) -> Stats:
        """
        Фабрика по умолчанию для создания Stats.
        
        Args:
            role: Роль персонажа.
            level: Уровень персонажа.
            base_stats_dict: Базовые характеристики.
            growth_rates_dict: Множители роста.
            config: Объект конфигурации игры (GameConfig).
            
        Returns:
            Экземпляр Stats.
        """
        level_multiplier = level * 0.1

        return SimpleStats(
            strength=int(base_stats_dict.get('strength', 10) * (1 + level_multiplier * growth_rates_dict.get('strength', 1.0))),
            agility=int(base_stats_dict.get('agility', 10) * (1 + level_multiplier * growth_rates_dict.get('agility', 1.0))),
            intelligence=int(base_stats_dict.get('intelligence', 10) * (1 + level_multiplier * growth_rates_dict.get('intelligence', 1.0))),
            vitality=int(base_stats_dict.get('vitality', 10) * (1 + level_multiplier * growth_rates_dict.get('vitality', 1.0))),
        )

    @staticmethod
    def default_attributes_factory(stats: Stats, config: 'GameConfig') -> Attributes:
        """Фабрика по умолчанию для создания Attributes."""
        attr = SimpleAttributes()
        attr.recalculate(stats, config)
        return attr

    # ==================== Вспомогательные методы ====================
    def _update_attributes(self, config: 'GameConfig') -> None:
        """Обновляет атрибуты на основе текущих характеристик."""
        #config = get_config()
        self.attributes.recalculate(self.stats, config)
        # Обновляем hp и энергию до максимума при пересчете
        self.health.restore_full_health()
        self.energy.restore_full_energy()

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

    def level_up(self) -> List[ActionResult]:
        """
        Повышает уровень персонажа.
        Возвращает список сообщений/результатов.
        """
        self.level += 1
        
        # Пересчитываем характеристики
        self.stats = self._stats_factory(self.role, self.level, self.base_stats_dict, self.growth_rates_dict)
        
        # Пересчитываем атрибуты
        self._update_attributes(self.game_config)
        
        # Возвращаем результат как ActionResult
        return [ActionResult(
            type="level_up",
            message=f"{self.name} достиг уровня {self.level}!"
        )]

    def on_death(self) -> List[ActionResult]:
        """
        Вызывается при смерти персонажа. 
        Возвращает список сообщений/результатов.
        """
        results: List[ActionResult] = []

        # Очищаем все активные статус-эффекты
        if self._status_manager is not None:
            clear_results = self._status_manager.clear_all_effects()
            results.extend(clear_results)

        # Добавляем сообщение о смерти
        results.append(ActionResult(type="death", message=f"{self.name} погибает!"))
        return results

    # ==================== Боевые методы ====================
    def take_damage(self, damage: int) -> List[ActionResult]:
        """
        Наносит урон персонажу, учитывая защиту.
        Возвращает список сообщений/результатов.
        """
        results = self.health.take_damage(damage, self.attributes.defense)
        
        # Обновляем имя в результатах
        for result in results:
            if hasattr(result, 'target'):
                result.target = self.name
        
        if not self.health.is_alive() and self.alive:
            self.alive = False
            death_results = self.on_death()
            results.extend(death_results)
            
        return results

    def take_heal(self, heal_amount: int) -> List[ActionResult]:
        """
        Исцеляет персонажа и возвращает список сообщений/результатов.
        """
        return self.health.take_heal(heal_amount)

    # ==================== Энергия ====================
    def restore_energy(self, amount: Optional[int] = None, 
        percentage: Optional[float] = None) -> List[ActionResult]:
        """
        Восстанавливает энергию персонажа.
        :param amount: конкретное количество энергии для восстановления
        :param percentage: процент от максимальной энергии для восстановления
        Возвращает список сообщений/результатов.
        """
        return self.energy.restore_energy(amount, percentage)

    def spend_energy(self, amount: int) -> bool:
        """
        Тратит энергию персонажа.
        Возвращает True, если энергия была потрачена, иначе False.
        """
        return self.energy.spend_energy(amount)

    # ==================== Способности ====================
    def add_ability(self, name: str, ability: Ability) -> List[ActionResult]:
        """Добавляет способность персонажу."""
        results: List[ActionResult] = []
        if self._ability_manager:
            self._ability_manager.add_ability(ability)
            results.append(ActionResult(
                type="ability_added",
                message=f"Способность {name} добавлена персонажу {self.name}"
            ))
        return results

    def get_available_abilities(self) -> List[Ability]:
        """Получает список доступных способностей."""
        if self._ability_manager:
            return self._ability_manager.get_available_abilities()
        return []

    def use_ability(self, name: str, targets: List['Character'], **kwargs) -> List[ActionResult]:
        """
        Использует способность по имени.
        Возвращает список сообщений/результатов от способности и менеджера.
        """
        results: List[ActionResult] = []
        if self._ability_manager:
            ability_result = self._ability_manager.use_ability(name, targets, **kwargs)
            if ability_result:
                if isinstance(ability_result, list):
                    results.extend(ability_result)
                else:
                    results.append(ability_result)
        return results

    def update_ability_cooldowns(self) -> List[ActionResult]:
        """Обновляет кулдауны способностей в конце раунда."""
        results: List[ActionResult] = []
        if self._ability_manager:
            results.append(ActionResult(
                type="cooldowns_updated",
                message=f"Кулдауны обновлены для персонажа {self.name}"
            ))
            self._ability_manager.update_cooldowns()
        return results

    # ==================== Статус-эффекты ====================
    def add_status_effect(self, effect: StatusEffect) -> List[ActionResult]:
        """Добавляет статус-эффект персонажу. Возвращает результат от менеджера."""
        if self._status_manager:
            return self._status_manager.apply_effect(effect)
        return []                  

    def remove_status_effect(self, effect_name: str) -> List[ActionResult]:
        """Удаляет статус-эффект по имени. Возвращает результат."""
        results: List[ActionResult] = []
        if self._status_manager:
            success = self._status_manager.remove_effect(effect_name)
            if success:
                results.append(ActionResult(type="effect_removed", message=f"Эффект {effect_name} удален у {self.name}"))
            else:
                results.append(ActionResult(type="error", message=f"Эффект {effect_name} не найден у {self.name}"))
        return results

    def update_status_effects(self) -> List[ActionResult]:
        """Обновляет все активные статус-эффекты. Возвращает список результатов."""
        if self._status_manager:
            return self._status_manager.update_effects()
        return []

    def has_status_effect(self, effect_name: str) -> bool:
        """Проверяет, есть ли у персонажа определенный статус-эффект."""
        if self._status_manager:
            return self._status_manager.get_effect(effect_name) is not None
        return False

    def get_active_status_effects(self) -> List[StatusEffect]:
        """Возвращает список всех активных статус-эффектов."""
        if self._status_manager:
            return self._status_manager.get_all_effects()
        return []