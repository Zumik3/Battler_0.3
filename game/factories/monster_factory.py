# game/factories/player_factory.py
"""Фабрика для создания персонажей-монстров."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
# Локальные импорты
from game.systems.character_loader import load_monster_class_data
from game.entities.character import CharacterConfig 
from game.entities.monster import Monster

if TYPE_CHECKING:
    from game.core.context import GameContext
    

@dataclass
class MonsterConfig(CharacterConfig):
    """Конфигурация для создания монстра."""
    
    is_player: bool = field(default=False)


class MonsterFactory:
    """Фабрика для создания экземпляров Monster."""

    @staticmethod
    def create_monster(context: 'GameContext', role: str, level: int = 1) -> Monster:
        """
        Создает объект Monster на основе данных из JSON файла.

        Args:
            context: Контекст игры.
            role: Внутренний идентификатор класса.
            level: Начальный уровень.

        Returns:
            Объект Monster.
            
        Raises:
            ValueError: Если данные конфигурации для роли не найдены.
        """
        config_data = load_monster_class_data(role=role)
        if config_data is None:
            raise ValueError(f"Configuration data for role '{role}' not found.")
            
        config = MonsterConfig(**config_data)
        monster = Monster(context=context, config=config)
        if level > 1:
            monster.level.level_up(level - 1)  # type: ignore
        return monster 
