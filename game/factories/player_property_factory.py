# game/factories/character_property_factory.py
"""Фабрика для создания и связывания всех свойств персонажа."""

from typing import  TYPE_CHECKING



from game.entities.properties.experience import ExperienceProperty
from game.factories.character_property_factory import CharacterPropertyFactory

if TYPE_CHECKING:
    from game.entities.player import Player
    from game.core.context import GameContext
    from game.entities.character import CharacterConfig

class PlayerPropertyFactory(CharacterPropertyFactory):
    """Фабрика для создания связанных свойств персонажа."""
    
    def __init__(self, context: 'GameContext', config: 'CharacterConfig', player: 'Player'):
        super().__init__(context)
        self.create_basic_properties(character=player, config=config)
        self.create_advanced_properties(player=player)
    
    def create_advanced_properties(self, player: 'Player') -> None:
        """Создает и связывает допольнительные свойства персонажа.
        
        Args:
            initial_data: Словарь с начальными данными для свойств
                         (например, начальные характеристики, уровень и т.д.).
                         
        Returns:
            Результат выполнения .
        """

        # 1. Создаем LevelProperty
        exp_prop = self._create_experience_property()
        
        # 6. Устанавливаем взаимные ссылки между Stats и Level для подписок
        exp_prop.level_property = player.level
        exp_prop._setup_subscriptions()

        player.level.exp_property = exp_prop # type: ignore
        player.level._setup_subscriptions() # type: ignore
        
        player.experience = exp_prop
    
    def _create_experience_property(self) -> ExperienceProperty:
        """Создает свойство опыта."""
        
        exp_prop = ExperienceProperty(
            context=self.property_context,
        )
        
        return exp_prop
