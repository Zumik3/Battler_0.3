# game/factories/monster_factory.py
"""Фабрика для создания монстров.

Предоставляет функции для создания экземпляров класса Character
на основе данных из JSON файлов, помеченных как не-игроки.
"""

import os
from typing import Optional, TYPE_CHECKING

# Импортируем функцию создания персонажа из загрузчика данных
from game.data.character_loader import create_character as _internal_create_character

# Импортируем Character только для аннотаций типов
if TYPE_CHECKING:
    from game.entities.character import Character

# Путь по умолчанию к данным монстров
DEFAULT_MONSTER_DATA_DIR = os.path.join("game", "data", "characters", "monster_classes")

def create_monster(
    name: str,
    role: str,
    level: int = 1,
    data_directory: str = DEFAULT_MONSTER_DATA_DIR
) -> Optional['Character']:
    """
    Создает объект монстра (Character с is_player=False) на основе данных из JSON файла.

    Args:
        name: Имя монстра.
        role: Внутренний идентификатор класса (должен совпадать с именем .json файла).
        level: Начальный уровень.
        data_directory: Путь к директории с JSON файлами.

    Returns:
        Объект Character (с is_player=False) или None, если данные не могут быть загружены.
    """
    return _internal_create_character(
        name=name,
        role=role,
        level=level,
        data_directory=data_directory,
        is_player=False # Явно указываем, что это не игрок
    )
