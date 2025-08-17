# game/factories/player_factory.py
"""Фабрика для создания персонажей-игроков."""

from typing import Optional, TYPE_CHECKING

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

    Args:
        role: Внутренний идентификатор класса.
        name: Имя персонажа.
        level: Начальный уровень.
        data_directory: Путь к директории с JSON файлами.
                        Если None, используется путь из конфигурации.

    Returns:
        Объект Player или None, если данные не могут быть загружены.
    """
    # Получаем директорию из конфигурации если не задана
    if data_directory is None:
        from game.config import get_config
        data_directory = get_config().system.player_classes_directory

    # Ленивый импорт для избежания циклических импортов
    from game.entities.player import create_player_from_data
    return create_player_from_data(
        role=role, 
        name=name, 
        level=level, 
        data_directory=data_directory
    )