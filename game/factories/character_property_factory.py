# game/factories/character_property_factory.py
"""Фабрика для создания и связывания всех свойств персонажа."""

from abc import ABC, abstractmethod
from typing import  Dict, Any

# Импорты контекстов и фабрик
from game.core.context import GameContext
from game.entities.character import Character
from game.entities.properties.context import GameContextBasedPropertyContext

# Импорты свойств
from game.entities.properties.stats import StatsProperty
from game.entities.properties.health import HealthProperty
from game.entities.properties.energy import EnergyProperty
from game.entities.properties.combat import CombatProperty
from game.entities.properties.experience import ExperienceProperty
from game.entities.properties.level import LevelProperty


class CharacterPropertyFactory(ABC):
    """Фабрика для создания связанных свойств персонажа."""
    
    @abstractmethod
    def __init__(self, game_context: GameContext):
        """
        Инициализирует фабрику свойств.
        
        Args:
            game_context: Глобальный контекст игры.
        """
        self.property_context = GameContextBasedPropertyContext(game_context)
    
    def create_basic_properties(self, character: Character, initial_data: Dict[str, Any] = {}) -> None:
        """Создает и связывает все свойства персонажа.
        
        Args:
            initial_data: Словарь с начальными данными для свойств
                         (например, начальные характеристики, уровень и т.д.).
                         
        Returns:
            Результат выполнения .
        """
        if initial_data is None:
            initial_data = {}
            
        # 1. Создаем StatsProperty (он не зависит от других свойств при создании)
        stats_prop = self._create_stats_property(initial_data.get('stats', {}))
        
        # 2. Создаем LevelProperty
        level_prop = self._create_level_property(initial_data.get('level', 1))
        
        # 3. Создаем HealthProperty, зависит от StatsProperty
        health_prop = self._create_health_property(stats_prop)
        
        # 4. Создаем EnergyProperty, зависит от StatsProperty
        energy_prop = self._create_energy_property(stats_prop)
        
        # 5. Создаем CombatProperty, зависит от StatsProperty
        combat_prop = self._create_combat_property(stats_prop)
        
        # 6. Устанавливаем взаимные ссылки между Stats и Level для подписок
        stats_prop.level_property = level_prop # type: ignore
        stats_prop._setup_subscriptions()
        
        character.stats = stats_prop
        character.level = level_prop
        character.health = health_prop
        character.energy = energy_prop
        character.combat = combat_prop

    
    def _create_stats_property(self, stats_data: Dict[str, int]) -> StatsProperty:
        """Создает свойство характеристик."""
        return StatsProperty(
            context=self.property_context,
            strength=stats_data.get('strength', 10),
            agility=stats_data.get('agility', 10),
            intelligence=stats_data.get('intelligence', 10),
            vitality=stats_data.get('vitality', 10),
            # level_property будет установлен позже
        )
    
    def _create_level_property(self, initial_level: int) -> LevelProperty:
        """Создает связанные свойства уровня и опыта."""
        
        # Сначала создаем оба свойства без ссылок друг на друга
        level_prop = LevelProperty(
            context=self.property_context,
            level=initial_level,
            # exp_property будет установлен позже
        )
        
        return level_prop
    
    def _create_health_property(self, stats_prop: StatsProperty) -> HealthProperty:
        """Создает свойство здоровья."""
        return HealthProperty(
            context=self.property_context,
            stats=stats_prop,
            # max_health и health будут рассчитаны автоматически
        )
    
    def _create_energy_property(self, stats_prop: StatsProperty) -> EnergyProperty:
        """Создает свойство энергии."""
        return EnergyProperty(
            context=self.property_context,
            stats=stats_prop,
            # max_energy и energy будут рассчитаны автоматически
        )
    
    def _create_combat_property(self, stats_prop: StatsProperty) -> CombatProperty:
        """Создает свойство боевых показателей."""
        return CombatProperty(
            context=self.property_context,
            stats=stats_prop,
            # attack_power и defence будут рассчитаны автоматически
        )
