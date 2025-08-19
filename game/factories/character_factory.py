# game/factories/character_factory.py
"""Базовая фабрика для создания персонажей."""

from typing import Dict, Any
from game.core.context import GameContext
from game.entities.character import Character
from game.factories.property_factory import PropertyFactory

class CharacterFactory:
    """Базовая фабрика для создания персонажей."""
    
    def create_character(self, name: str, role: str, context: GameContext, 
                        character_ dict) -> Character:
        """
        Шаблонный метод создания персонажа.
        
        Args:
            name: Имя персонажа
            role: Роль персонажа  
            context: Игровой контекст
            character_data: Данные для создания персонажа
            
        Returns:
            Созданный персонаж
        """
        # 1. Создаем экземпляр
        character = self._create_instance(name, role, context)
        
        # 2. Создаем стандартные свойства
        properties = self._create_standard_properties(character_data, context)
        
        # 3. Добавляем специфичные свойства
        self._add_specific_properties(character, properties, character_data, context)
        
        # 4. Устанавливаем свойства
        self._set_properties(character, properties)
        
        return character
    
    def _create_instance(self, name: str, role: str, context: GameContext) -> Character:
        """Создает базовый экземпляр персонажа."""
        return Character(name, role, context)
    
    def _create_standard_properties(self, character_ dict, context: GameContext) -> Dict[str, Any]:
        """Создает стандартный набор свойств."""
        return PropertyFactory.create_standard_properties(character_data, context)
    
    def _add_specific_properties(self, character: Character, properties: Dict[str, Any], 
                               character_ dict, context: GameContext) -> None:
        """Добавляет специфичные свойства (переопределяется в подклассах)."""
        pass  # Базовая реализация - ничего не добавляет
    
    def _set_properties(self, character: Character, properties: Dict[str, Any]) -> None:
        """Устанавливает свойства персонажу."""
        for prop_name, prop_obj in properties.items():
            if hasattr(character, prop_name):
                setattr(character, prop_name, prop_obj)