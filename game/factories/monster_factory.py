# game/factories/monster_factory.py
"""Фабрика для создания монстров.

Предоставляет функции для создания экземпляров класса Monster
на основе данных из JSON файлов.
"""

from typing import TYPE_CHECKING, Optional, Union
from game.naming.template_namer import generate_monster_name
from game.data.character_loader import _get_default_data_directory

if TYPE_CHECKING:
    from game.entities.monster import Monster

def create_monster(
    role: str,
    name: Optional[str] = None,
    level: int = 1,
    data_directory: Optional[str] = None
) -> Union['Monster', None]:
    """
    Создает монстра по его роли (типу).

    Args:
        role: Внутренний идентификатор класса монстра (должен совпадать с именем .json файла).
        name: Имя монстра. Если None или пустая строка, будет сгенерировано автоматически.
        level: Уровень монстра.
        data_directory: Путь к директории с JSON файлами классов монстров.

    Returns:
        Объект Character (Monster) или None, если данные не могут быть загружены.
    """

    if data_directory is None:
        data_directory = _get_default_data_directory(is_player=False)

    if not name or not name.strip():
        name = generate_monster_name(role)


    # Импортируем внутри функции
    from game.entities.monster import create_monster_from_data as _internal_create
    return _internal_create(role=role, name=name, level=level, data_directory=data_directory)
