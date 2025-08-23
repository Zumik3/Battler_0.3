# game/factories/character_property_factory.py
"""Фабрика для создания и связывания всех свойств персонажа."""

from abc import ABC, abstractmethod
from typing import  Dict, Any

# Импорты контекстов и фабрик
from game.core.context import GameContext
from game.entities.character import Character, CharacterConfig
from game.entities.properties.property_context import GameContextBasedPropertyContext

# Импорты свойств
from game.entities.properties.stats import StatsProperty
from game.entities.properties.health import HealthProperty
from game.entities.properties.energy import EnergyProperty
from game.entities.properties.combat import CombatProperty
from game.entities.properties.level import LevelProperty
from game.entities.properties.stats_config import BaseStats, GrowthRates, StatsConfigProperty
from game.events.character import HealthChangedEvent


class CharacterPropertyFactory(ABC):
    """Фабрика для создания связанных свойств персонажа."""
    
    @abstractmethod
    def __init__(self, context: GameContext, character: 'Character'):
        """
        Инициализирует фабрику свойств.
        
        Args:
            game_context: Глобальный контекст игры.
        """
        self.context = GameContextBasedPropertyContext(character=character)
    
    def create_basic_properties(self, 
        character: 'Character', 
        config: 'CharacterConfig') -> None:
        """Создает и связывает все свойства персонажа.
        
        Args:
            initial_data: Словарь с начальными данными для свойств
                         (например, начальные характеристики, уровень и т.д.).
                         
        Returns:
            Результат выполнения .
        """
        # 0. Создаем конфиг свойств для обновления статс
        # это свойство живет внутри статс - и не учествует в интеграциях с шиной
        stats_config_prop = self._create_stat_config_property(config)

        # 1. Создаем LevelProperty
        level_prop = self._create_level_property(1)

        # 2. Создаем StatsProperty
        stats_prop = self._create_stats_property(
            level_source=level_prop, 
            stats_config=stats_config_prop
        )
        
        # 3. Создаем HealthProperty, зависит от StatsProperty
        health_prop = self._create_health_property(stats_prop)
        
        # 4. Создаем EnergyProperty, зависит от StatsProperty
        energy_prop = self._create_energy_property(stats_prop)
        
        # 5. Создаем CombatProperty, зависит от StatsProperty
        combat_prop = self._create_combat_property(stats_prop)
        
        character.stats = stats_prop
        character.level = level_prop
        character.health = health_prop
        character.energy = energy_prop
        character.combat = combat_prop

        # --- НОВОЕ: Настройка подписок персонажа ---
        self._setup_character_subscriptions(character)

    def _create_stat_config_property(self, config: 'CharacterConfig'):
        return StatsConfigProperty(
            base_stats=BaseStats(**config.base_stats),
            growth_rates=GrowthRates(**config.growth_rates)
        )
    
    def _create_stats_property(self, level_source: LevelProperty, stats_config: 'StatsConfigProperty') -> StatsProperty:
        """Создает свойство характеристик."""
        return StatsProperty(
            context=self.context,
            stats_config=stats_config,
            strength=10,
            agility=10,
            intelligence=10,
            vitality=10,
            level_source = level_source)
    
    def _create_level_property(self, initial_level: int) -> LevelProperty:
        """Создает связанные свойства уровня и опыта."""
        
        # Сначала создаем оба свойства без ссылок друг на друга
        level_prop = LevelProperty(
            context=self.context,
            level=initial_level,
            # exp_property будет установлен позже
        )
        
        return level_prop
    
    def _create_health_property(self, stats_prop: StatsProperty) -> HealthProperty:
        """Создает свойство здоровья."""
        return HealthProperty(
            context=self.context,
            stats=stats_prop,
            # max_health и health будут рассчитаны автоматически
        )
    
    def _create_energy_property(self, stats_prop: StatsProperty) -> EnergyProperty:
        """Создает свойство энергии."""
        return EnergyProperty(
            context=self.context,
            stats=stats_prop,
            # max_energy и energy будут рассчитаны автоматически
        )
    
    def _create_combat_property(self, stats_prop: StatsProperty) -> CombatProperty:
        """Создает свойство боевых показателей."""
        return CombatProperty(
            context=self.context,
            stats=stats_prop,
            # attack_power и defence будут рассчитаны автоматически
        )

    def _setup_character_subscriptions(self, character: 'Character') -> None:
            """
            Настраивает подписки персонажа на события после создания всех свойств.
            
            Args:
                character: Экземпляр персонажа, для которого настраиваются подписки.
            """
            if character.health and self.context.event_bus:
                event_bus = self.context.event_bus
                
                event_bus.subscribe(
                    character.health,  # Источник событий - HealthProperty персонажа
                    HealthChangedEvent, # Тип события
                    character._on_health_changed # Метод-обработчик у персонажа
                )
                print(f"  Character '{character.name}' subscribed to HealthChangedEvent from its HealthProperty#{id(character.health)}")
