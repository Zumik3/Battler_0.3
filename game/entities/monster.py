# game/entities/monster.py
"""Класс монстра (персонажа, НЕ управляемого игроком)."""

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
from game.entities.character import Character, CharacterConfig

if TYPE_CHECKING:
    from game.entities.character import Character as CharacterType

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
        config = MonsterConfig(**config_data)
        config.level = level
        config.name = name if name else config.name
        config.is_player = False  # Явно указываем
        return Monster(config)

    except Exception as e:
        print(f"Ошибка создания монстра {name} класса {role}: {e}")
        import traceback
        traceback.print_exc()
        return None

class Monster(Character):
    """Класс для всех монстров (персонажей, НЕ управляемых игроком)."""

    def __init__(self, config: MonsterConfig):
        """
        Инициализирует монстра.

        Args:
            config: Конфигурация монстра.
        """
        super().__init__(config=config)
        
        # Здесь можно добавить специфичную для монстров логику
        # Например:
        # self.ai_behavior = config.ai_behavior if hasattr(config, 'ai_behavior') else 'aggressive'