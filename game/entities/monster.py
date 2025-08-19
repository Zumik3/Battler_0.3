# game/entities/monster.py
"""Класс монстра (персонажа, НЕ управляемого игроком)."""

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from game import config
from game.entities.character import Character, CharacterConfig

if TYPE_CHECKING:
    from game.entities.character import Character as CharacterType
    from game.config import GameConfig

# MonsterConfig можно не создавать - используем CharacterConfig
# или если нужна специфика:
@dataclass
class MonsterConfig(CharacterConfig):
    """Конфигурация для создания монстра."""
    pass  # Пока нет специфичных параметров

def create_monster_from_data(
    role: str,
    name: str,
    level: int = 1,
    data_directory: Optional[str] = None
) -> Optional['Monster']:
    """
    Создает объект Monster на основе данных из JSON файла.

    Args:
        role: Внутренний идентификатор класса.
        name: Имя монстра.
        level: Начальный уровень.
        data_directory: Путь к директории с JSON файлами.

    Returns:
        Объект Monster или None, если данные не могут быть загружены.
    """
    if data_directory is None:
        from game.config import get_config
        data_directory = get_config().system.monster_classes_directory
        
    try:
        from game.data.character_loader import load_monster_class_data
    except ImportError as e:
        print(f"Ошибка импорта character_loader: {e}")
        return None

    config_data = load_monster_class_data(role, data_directory)
    if not config_data:
        print(f"Не удалось загрузить данные для класса монстра '{role}'")
        return None

    try:
        character_config = MonsterConfig(**config_data)
        character_config.level = level
        character_config.name = name if name else character_config.name
        character_config.is_player = False  # Явно указываем

        game_config = config.get_config()

        return Monster(character_config=character_config, game_config=game_config)

    except Exception as e:
        print(f"Ошибка создания монстра {name} класса {role}: {e}")
        import traceback
        traceback.print_exc()
        return None

class Monster(Character):
    """Класс для всех монстров (персонажей, НЕ управляемых игроком)."""

    def __init__(self, character_config: MonsterConfig, game_config: 'GameConfig'):
        """
        Инициализирует монстра.

        Args:
            config: Конфигурация монстра.
        """
        super().__init__(character_config=character_config, game_config=game_config)
        
        # Здесь можно добавить специфичную для монстров логику
        # Например:
        # self.ai_behavior = config.ai_behavior if hasattr(config, 'ai_behavior') else 'aggressive'