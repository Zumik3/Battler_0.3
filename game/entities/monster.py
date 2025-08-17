# game/entities/monster.py
"""Класс монстра (персонажа, НЕ управляемого игроком)."""
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from game.entities.character import Character, CharacterConfig # Импортируем вспомогательные классы

if TYPE_CHECKING:
    from game.entities.character import Character as CharacterType


@dataclass
class MonsterConfig(CharacterConfig):
    is_player: bool = field(default=False)

# - Фабричная функция для создания монстра из JSON -
def create_monster_from_data(
    role: str,
    name: str,
    level: int = 1,
    data_directory: str = "game/data/characters/monster_classes"
) -> Optional['Monster']:
    """
    Создает объект Monster на основе данных из JSON файла.

    Args:
        name: Имя монстра.
        role: Внутренний идентификатор класса (должен совпадать с именем .json файла).
        level: Начальный уровень.
        data_directory: Путь к директории с JSON файлами.

    Returns:
        Объект Monster или None, если данные не могут быть загружены.
    """
    try:
        from game.data.character_loader import load_monster_class_data
    except ImportError as e:
        print(f"Ошибка импорта character_loader внутри create_monster_from_data: {e}")
        return None

    config_data = load_monster_class_data(role, data_directory)
    if not config_data:
        print(f"Не удалось загрузить данные для класса монстра '{role}'")
        return None

    try:
        config = MonsterConfig(**config_data)
        config.name = name if name else config.name
        return Monster(config)

    except Exception as e:
        print(f"Ошибка создания монстра {name} класса {role}: {e}")
        import traceback
        traceback.print_exc()
        return None

# --- Основной класс монстра ---

class Monster(Character):
    """Класс для всех монстров (персонажей, НЕ управляемых игроком)."""

    def __init__(self, config: MonsterConfig):  
        super().__init__(config=config)

