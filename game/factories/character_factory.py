# # game/factories/character_factory.py
# """Базовая фабрика для создания персонажей."""

# from abc import ABC, abstractmethod
# from typing import Dict, Any
# from game.config import GameConfig
# from game.core.context import GameContext
# from game.entities.character import Character

# class CharacterFactory(ABC):
#     """Базовая фабрика для создания персонажей."""
    

#     def create_character(self, context: 'GameContext', role: str) -> Character:
#         """
#         Шаблонный метод создания персонажа.
        
#         Args:
#             name: Имя персонажа
#             role: Роль персонажа  
#             context: Игровой контекст
#             character_data: Данные для создания персонажа
            
#         Returns:
#             Созданный персонаж
#         """
#         # 1. Создаем экземпляр
#         character_config = 

#         character = self._create_instance(name, role, context)
        
#         # 2. Создаем стандартные свойства
#         properties = self._create_standard_properties(character_data, context)
        
#         # 3. Добавляем специфичные свойства
#         self._add_specific_properties(character, properties, character_data, context)
        
#         # 4. Устанавливаем свойства
#         self._set_properties(character, properties)
        
#         return character
    
#     def _create_instance(self, name: str, role: str, context: GameContext) -> Character:
#         """Создает базовый экземпляр персонажа."""
#         return Character(context, config)

#     @abstractmethod
#     def create_character_config(self, game_config: GameConfig):
#         pass
