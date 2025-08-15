# game/data/character_loader.py
"""
Загрузчик данных персонажей из JSON файлов.
"""

import json
import os
from typing import Dict, Any, Optional, TYPE_CHECKING

from game.config import SystemSettings

# Используем TYPE_CHECKING для аннотаций без циклического импорта на уровне модуля
if TYPE_CHECKING:
    from game.entities.player import Player


def load_player_class_data(role: str, 
    data_directory: str = SystemSettings.player_classes_directory) -> Optional[Dict[str, Any]]:
    """
    Загружает данные класса игрока из JSON файла.

    Args:
        role: Внутренний идентификатор класса (например, "berserker").
        data_directory: Путь к директории с JSON файлами.

    Returns:
        Словарь с данными класса или None, если файл не найден.
    """
    filename = f"{role}.json"
    filepath = os.path.join(data_directory, filename)

    # Проверяем, существует ли файл
    if not os.path.exists(filepath):
        # Пробуем относительный путь от корня проекта, если предыдущий не сработал
        # Это может помочь, если скрипт запускается не из корня проекта
        try:
            # Получаем путь к корню проекта (предполагаем, что loader.py находится в game/data/)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            filepath = os.path.join(project_root, data_directory, filename)
            if not os.path.exists(filepath):
                print(f"Файл данных для класса '{role}' не найден: {filepath}")
                return None
        except Exception as e:
            print(f"Ошибка при определении пути к файлу {filename}: {e}")
            return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON в файле {filepath}: {e}")
        return None
    except Exception as e:
        print(f"Неизвестная ошибка при загрузке {filepath}: {e}")
        return None


def create_player(
    name: str, 
    role: str, 
    level: int = 1,
    data_directory: str = "game/data/characters/player_classes"
) -> Optional['Player']:
    """
    Создает объект Player на основе данных из JSON файла.
    Упрощенный интерфейс для game.entities.player.create_player_from_data.

    Args:
        name: Имя персонажа.
        role: Внутренний идентификатор класса.
        level: Начальный уровень.
        data_directory: Путь к директории с JSON файлами.

    Returns:
        Объект Player или None, если данные не могут быть загружены.
    """
    # Отложенная загрузка, чтобы избежать циклического импорта на уровне модуля
    try:
        # Импортируем внутри функции
        from game.entities.player import create_player_from_data as _internal_create
        return _internal_create(name, role, level, data_directory)
    except ImportError as e:
        print(f"Ошибка импорта при создании игрока: {e}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка при создании игрока {name} класса {role}: {e}")
        import traceback
        traceback.print_exc()
        return None
