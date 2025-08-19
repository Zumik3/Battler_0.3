# game/entities/character.py
"""Базовый класс персонажа в игре."""

from abc import ABC
from dataclasses import dataclass, field
from typing import List, Dict, Optional, TYPE_CHECKING

from game.config import GameConfig
from game.results import ActionResult

if TYPE_CHECKING:
    from game.entities.properties.combat import CombatProperty
    from game.entities.properties.health import HealthProperty
    from game.entities.properties.energy import EnergyProperty
    from game.entities.properties.level import LevelProperty
    from game.entities.properties.stats import StatsProperty
    from game.core.context import GameContext


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


# ==================== Основной класс персонажа ====================
class Character(ABC):
    """Абстрактный базовый класс, представляющий персонажа в игре."""

    # Объявляем атрибуты на уровне класса для mypy
    context: 'GameContext'
    name: str
    role: str
    alive: bool
    is_player: bool
    class_icon: str
    class_icon_color: str
    base_stats_dict: Dict[str, int]
    growth_rates_dict: Dict[str, float]
    
    # Атрибуты, которые будут заполнены фабрикой свойств
    stats: Optional['StatsProperty']
    level: Optional['LevelProperty']
    health: Optional['HealthProperty']
    energy: Optional['EnergyProperty']
    combat: Optional['CombatProperty']

    def __init__(self, context: 'GameContext', config: 'CharacterConfig'):

        self.context = context

        self.alive = True
        self.name = config.name
        self.role = config.role
        self.is_player = config.is_player

        self.class_icon = config.class_icon
        self.class_icon_color = config.class_icon_color

        self.base_stats_dict = config.base_stats
        self.growth_rates_dict = config.growth_rates

        # Используем фабрики из конфига или по умолчанию
        #self._stats_factory = character_config.stats_factory or (lambda role, level, base, growth: Character.default_stats_factory(role, level, base, growth))
        #self._attributes_factory = character_config.attributes_factory or (lambda stats, config_obj: Character.default_attributes_factory(stats, config_obj))

        # Инициализация характеристик
        #self.stats: Stats = self._stats_factory(self.role, self.level, self.base_stats_dict, self.growth_rates_dict)
        #self.attributes: Attributes = self._attributes_factory(self.stats, game_config)

        # Инициализируем hp и энергию
        #self.health = HealthProperty(self.attributes.max_hp, 0)
        #self.energy = EnergyProperty(self.attributes.max_energy, 0)

        # Менеджеры (внедрение зависимостей)
        # self._ability_manager: Optional[AbilityManagerProtocol] = None
        # if character_config.ability_manager_factory:
        #     self._ability_manager = character_config.ability_manager_factory(self)

        # self._status_manager: Optional[StatusEffectManagerProtocol] = None
        # if character_config.status_effect_manager_factory:
        #     self._status_manager = character_config.status_effect_manager_factory(self)

    # ==================== Основные методы персонажа ====================
    def is_alive(self) -> bool:
        """Проверяет, жив ли персонаж."""
        return self.alive
