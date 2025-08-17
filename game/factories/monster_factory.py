# game/factories/monster_factory.py
"""Фабрика для создания монстров."""

from typing import TYPE_CHECKING, Optional
from game.naming.template_namer import generate_monster_name

if TYPE_CHECKING:
    from game.entities.monster import Monster

def create_monster(
    role: str,
    name: Optional[str] = None,
    level: int = 1,
    data_directory: Optional[str] = None
) -> Optional['Monster']:
    """
    Создает монстра по его роли (типу).

    Args:
        role: Внутренний идентификатор класса монстра.
        name: Имя монстра. Если None, будет сгенерировано автоматически.
        level: Уровень монстра.
        data_directory: Путь к директории с JSON файлами классов монстров.

    Returns:
        Объект Monster или None, если данные не могут быть загружены.
    """
    # Получаем директорию из конфигурации если не задана
    if data_directory is None:
        from game.config import get_config
        data_directory = get_config().system.monster_classes_directory

    # Генерируем имя если не задано
    if not name or not name.strip():
        name = generate_monster_name(role)

    # Ленивый импорт для избежания циклических импортов
    from game.entities.monster import create_monster_from_data
    return create_monster_from_data(
        role=role, 
        name=name, 
        level=level, 
        data_directory=data_directory
    )