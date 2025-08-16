# game/factories/player_factory.py
"""Фабрика для создания персонажей-игроков.

Предоставляет функции для создания экземпляров класса Player
на основе данных из JSON файлов.
"""

from typing import Optional, TYPE_CHECKING

# Импортируем функцию создания игрока из загрузчика данных
# Это предотвращает циклический импорт, так как сам Player импортирует из character_loader
from game.data.character_loader import create_player as _internal_create_player

# Импортируем Player только для аннотаций типов
if TYPE_CHECKING:
    from game.entities.player import Player


def create_player(
    name: str,
    role: str,
    level: int = 1,
    data_directory: str = "game/data/characters/player_classes"
) -> Optional['Player']:
    """
    Создает объект Player на основе данных из JSON файла.

    Args:
        name: Имя персонажа.
        role: Внутренний идентификатор класса (должен совпадать с именем .json файла).
        level: Начальный уровень.
        data_directory: Путь к директории с JSON файлами.

    Returns:
        Объект Player или None, если данные не могут быть загружены.
    """
    # Просто переэкспортируем функцию из character_loader
    # для соответствия структуре импортов (factories.player_factory)
    return _internal_create_player(
        name=name,
        role=role,
        level=level,
        data_directory=data_directory
    )
