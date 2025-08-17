# game/factories/player_factory.py
"""Фабрика для создания персонажей-игроков.

Предоставляет функции для создания экземпляров класса Player
на основе данных из JSON файлов.
"""

from typing import Optional, TYPE_CHECKING
from game.data.character_loader import _get_default_data_directory

if TYPE_CHECKING:
    from game.entities.player import Player


def create_player(
    role: str,
    name: str, 
    level: int = 1,
    data_directory: Optional[str] = None
    ) -> Optional['Player']:
    """
    Создает объект Player на основе данных из JSON файла.
    Упрощенный интерфейс для game.entities.player.create_player_from_data.

    Args:
        role: Внутренний идентификатор класса.
        name: Имя персонажа.
        level: Начальный уровень.
        data_directory: Путь к директории с JSON файлами.
                        Если None, используется путь из конфигурации.

    Returns:
        Объект Player или None, если данные не могут быть загружены.
    """
    if data_directory is None:
        data_directory = _get_default_data_directory(is_player=True)

    from game.entities.player import create_player_from_data as _internal_create
    return _internal_create(role, name, level, data_directory)
