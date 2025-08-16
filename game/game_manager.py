# game/game_manager.py
"""Менеджер игрового состояния.
Отвечает за инициализацию и хранение основных сущностей игры:
игроков, глобального состояния, текущих врагов, инвентаря и т.д.
Реализует паттерн Singleton для обеспечения единственного экземпляра менеджера."""

from typing import List, Optional, TYPE_CHECKING
import json
import os

from game.factories.player_factory import create_player
from game.config import get_config

if TYPE_CHECKING:
    from game.entities.player import Player
    from game.entities.monster import Monster
    # from game.inventory import Inventory # и т.д.


class GameManager:
    """Менеджер игрового состояния."""
    _instance: Optional['GameManager'] = None # Для реализации Singleton

    def __new__(cls) -> 'GameManager':
        """Реализация паттерна Singleton."""
        if cls._instance is None:
            cls._instance = super(GameManager, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Инициализирует менеджер игры и загружает начальное состояние."""
        # Проверка, инициализирован ли уже объект, чтобы избежать повторной инициализации
        # при повторном вызове __init__ на том же экземпляре из-за Singleton
        if hasattr(self, 'initialized'):
            return

        self.config = get_config() # Получаем глобальную конфигурацию

        # --- Инициализация основных сущностей ---
        self.player_group: List['Player'] = []
        self.current_enemies: List['Monster'] = []
        # self.global_inventory: 'Inventory' = ... # Для будущего использования

        self._initialize_game_entities()

        self.initialized = True # Флаг, что инициализация прошла

    def _initialize_game_entities(self) -> None:
        """Создает и инициализирует стартовые сущности игры."""
        # --- Создание стартовой группы игроков ---
        print("Инициализация стартовой группы игроков...")
        
        # Получаем пути из конфигурации
        player_data_dir = self.config.system.player_classes_directory

        # Пример создания игроков
        # В будущем это может загружаться из файла сохранения или профиля
        
        # Создаем Берсерка
        berserker = create_player(
            name="Громила",
            role="berserker",
            level=1,
            data_directory=player_data_dir
        )
        if berserker:
            self.player_group.append(berserker)

        # Создаем Лекаря
        healer = create_player(
            name="Целитель",
            role="healer",
            level=1,
            data_directory=player_data_dir
        )
        if healer:
            self.player_group.append(healer)


        # TODO: Добавить создание других стартовых игроков, если нужно
        # --- Инициализация других сущностей ---
        # TODO: Инициализация инвентаря, глобального состояния и т.д.

    def get_player_group(self) -> List['Player']:
        """Получить текущую группу игроков."""
        return self.player_group

    # TODO: Добавить методы для управления другими сущностями
    # def get_current_enemies(self) -> List['Monster']: ...
    # def get_global_inventory(self) -> 'Inventory': ...
    # def start_new_battle(self, enemies: List['Monster']) -> None: ...
    # и т.д.

# Функция для удобного получения экземпляра GameManager
def get_game_manager() -> GameManager:
    """Получить глобальный экземпляр GameManager."""
    # Это гарантирует, что экземпляр будет создан при первом вызове
    return GameManager()
