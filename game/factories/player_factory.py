# game/factories/player_factory.py
"""Фабрика для создания персонажей-игроков."""

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from game.data.character_loader import load_player_class_data
from game.entities.character import CharacterConfig
from game.entities.player import Player

if TYPE_CHECKING:
    from game.core.context import GameContext
    

@dataclass
class PlayerConfig(CharacterConfig):
    """Конфигурация для создания игрока."""
    is_player: bool = field(default=True)


class PlayerFactory():

    @staticmethod
    def create_player(context: 'GameContext', role: str, level: int = 1) -> Optional['Player']:
        """
        Создает объект Player на основе данных из JSON файла.

        Args:
            role: Внутренний идентификатор класса.
            level: Начальный уровень.

        Returns:
            Объект Player или None, если данные не могут быть загружены.
        """
        config_data = load_player_class_data(role=role)
        if config_data is None:
            raise ValueError(f"Configuration data for role '{role}' not found.")
        config = PlayerConfig(**config_data)

        return Player(context=context, config=config)