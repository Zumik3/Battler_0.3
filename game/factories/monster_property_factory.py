# game/factories/character_property_factory.py
"""Фабрика для создания и связывания всех свойств монстра."""

from typing import  TYPE_CHECKING


from game.factories.character_property_factory import CharacterPropertyFactory

if TYPE_CHECKING:
    from game.entities.monster import Monster
    from game.core.character_context import CharacterContext
    from game.entities.character import CharacterConfig
    from game.core.game_context import GameContext

class MonsterPropertyFactory(CharacterPropertyFactory):
    """Фабрика для создания связанных свойств монстра."""
    
    def __init__(self, context: 'CharacterContext', game_context: 'GameContext', config: 'CharacterConfig', monster: 'Monster'):
        super().__init__(context=context, game_context=game_context, character=monster)
        self.create_basic_properties(character=monster, game_context=game_context, config=config)
    
    def create_advanced_properties(self, monster: 'Monster') -> None:
        """Создает и связывает допольнительные свойства монстра.
        
        Args:
            initial_data: Словарь с начальными данными для свойств
                         (например, начальные характеристики, уровень и т.д.).
                         
        Returns:
            Результат выполнения .
        """
        pass

        
    