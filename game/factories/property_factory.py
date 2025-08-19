# game/factories/property_factory.py
"""Фабрика для создания свойств персонажа."""

from typing import Dict, Any
from game.core.context import GameContext
from game.entities.properties.base import BaseProperty

class PropertyFactory:
    """Фабрика для создания свойств персонажа."""
    
    @staticmethod
    def create_standard_properties(context: GameContext) -> Dict[str, BaseProperty]:
        """
        Создает стандартный набор свойств для персонажа.
        
        Args:
            character_ Данные персонажа
            context: Игровой контекст
            
        Returns:
            Словарь свойств {имя: объект_свойства}
        """
        from game.entities.properties.level import LevelProperty
        from game.entities.properties.stats import StatsProperty
        from game.entities.properties.health import HealthProperty
        from game.entities.properties.energy import EnergyProperty
        from game.entities.properties.combat import CombatProperty
        
        properties: Dict[str, BaseProperty] = {}
        
        # 1. Создаем уровень (базовое свойство)
        level_prop = LevelProperty(
            level=character_data.get('level', 1)
        )
        properties['level'] = level_prop
        
        # 2. Создаем характеристики (зависит от уровня)
        stats_prop = StatsProperty(
            base_stats=character_data.get('base_stats', {}),
            growth_rates=character_data.get('growth_rates', {}),
            level_property=level_prop  # Связываем с уровнем
        )
        properties['stats'] = stats_prop
        
        # 3. Создаем здоровье (зависит от статов)
        health_prop = HealthProperty(stats=stats_prop)
        properties['health'] = health_prop
        
        # 4. Создаем энергию (зависит от статов)
        energy_prop = EnergyProperty(stats=stats_prop)
        properties['energy'] = energy_prop
        
        # 5. Создаем боевые показатели (зависит от статов)
        combat_prop = CombatProperty(stats=stats_prop)
        properties['combat'] = combat_prop
        
        return properties