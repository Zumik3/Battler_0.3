# game/data/character_loader.py
"""Загрузчик данных персонажей из JSON файлов."""

import json
import os
from typing import Dict, Any, Optional, TYPE_CHECKING

# Используем TYPE_CHECKING для аннотаций без циклического импорта на уровне модуля
if TYPE_CHECKING:
    from game.config import GameConfig # Для аннотаций


# --- Вспомогательные (приватные) функции ---
def _get_default_data_directory(is_player: bool) -> str:
    """
    Получает путь к директории данных по умолчанию из конфигурации.

    Args:
        is_player: Если True, возвращает путь для игроков.
                   Если False, возвращает путь для монстров.

    Returns:
        Путь к директории данных.
    """
    from game.config import get_config # Локальный импорт
    config: 'GameConfig' = get_config()

    if is_player:
        return config.system.player_classes_directory
    else:
        return config.system.monster_classes_directory


def _load_character_data_from_file(
    role: str, 
    data_directory: str
    ) -> Optional[Dict[str, Any]]:
    """
    Загружает данные класса персонажа из JSON файла.

    Args:
        role: Внутренний идентификатор класса (например, "berserker", "goblin").
        data_directory: Путь к директории с JSON файлами.

    Returns:
        Словарь с данными класса или None, если файл не найден или произошла ошибка.
    """
    filename = f"{role}.json"
    filepath = os.path.join(data_directory, filename)

    # Проверяем, существует ли файл
    if not os.path.exists(filepath):
        # Пробуем относительный путь от корня проекта, если предыдущий не сработал
        # Это может помочь, если скрипт запускается не из корня проекта
        try:
            # Получаем путь к корню проекта (предполагаем, что loader.py находится в game/data/)
            # os.path.abspath(__file__) дает полный путь к этому файлу
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


# --- Публичные функции для игроков ---
def load_player_class_data(
    role: str, 
    data_directory: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
    """
    Загружает данные класса игрока из JSON файла.

    Args:
        role: Внутренний идентификатор класса (например, "berserker").
        data_directory: Путь к директории с JSON файлами.
                        Если None, используется путь из конфигурации.

    Returns:
        Словарь с данными класса или None, если файл не найден.
    """
    if data_directory is None:
        data_directory = _get_default_data_directory(is_player=True)
        
    return _load_character_data_from_file(role, data_directory)


# --- Публичные функции для монстров ---
def load_monster_class_data(
    role: str, 
    data_directory: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
    """
    Загружает данные класса монстра из JSON файла.

    Args:
        role: Внутренний идентификатор класса монстра (например, "goblin").
        data_directory: Путь к директории с JSON файлами.
                        Если None, используется путь из конфигурации.

    Returns:
        Словарь с данными класса или None, если файл не найден.
    """
    if data_directory is None:
        data_directory = _get_default_data_directory(is_player=False)
        
    return _load_character_data_from_file(role, data_directory)
