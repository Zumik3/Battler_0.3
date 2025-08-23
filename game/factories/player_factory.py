# game/factories/player_factory.py
"""Фабрика для создания персонажей-игроков."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from game.systems.data.character_loader import load_player_class_data
from game.entities.character import CharacterConfig 
from game.entities.player import Player

if TYPE_CHECKING:
    from game.core.character_context import CharacterContext
    

@dataclass
class PlayerConfig(CharacterConfig):
    """Конфигурация для создания игрока."""
    
    is_player: bool = field(default=True)


class PlayerFactory:
    """Фабрика для создания экземпляров Player."""

    @staticmethod
    def create_player(context: 'CharacterContext', role: str, level: int = 1) -> Player:
        """
        Создает объект Player на основе данных из JSON файла.

        Args:
            context: Контекст игры.
            role: Внутренний идентификатор класса.
            level: Начальный уровень.

        Returns:
            Объект Player.
            
        Raises:
            ValueError: Если данные конфигурации для роли не найдены.
        """
        config_data = load_player_class_data(role=role)
        if config_data is None:
            raise ValueError(f"Configuration data for role '{role}' not found.")
            
        config = PlayerConfig(**config_data)
        return Player(context=context, config=config)
