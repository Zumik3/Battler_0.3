# game/game_manager.py
"""Менеджер игрового состояния.
Отвечает за инициализацию и хранение основных сущностей игры:
игроков, глобального состояния, текущих врагов, инвентаря и т.д.
Реализует паттерн Singleton для обеспечения единственного экземпляра менеджера."""

from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union

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
        # Получаем пути из конфигурации
        player_data_dir = self.config.system.player_classes_directory
        # monster_data_dir = self.config.system.monster_classes_directory # Если понадобится напрямую

        # --- Инициализация игроков ---
        # В будущем это может загружаться из файла сохранения или профиля
        
        # Словарь с именами и ролями стартовых игроков
        starting_players = {
            "Роланд": "berserker",
            "Стайлс": "rogue"
            #"Морган": "mage",
            #"Дамиан": "healer"
        }
        
        # Создаем каждого игрока из словаря
        for name, role in starting_players.items():
            player = create_player(
                role=role,
                name=name,
                level=1,
                data_directory=player_data_dir
            )
            if player:
                self.player_group.append(player)

        # --- Инициализация стартовых врагов ---
        # Создаем начальную группу врагов для первого боя
        # Пример данных для создания монстров
        initial_enemy_data = [
            {'role': 'goblin', 'level': 1}, # Имя будет сгенерировано
            {'role': 'orc', 'name': 'Громозека', 'level': 2},
            # Можно добавить больше стартовых монстров
        ]
        
        # Создаем монстров, используя существующий метод create_enemies
        # Это заполнит self.current_enemies
        self.create_enemies(initial_enemy_data)
        
        # Альтернатива: можно вызвать create_monster напрямую в цикле,
        # но использование create_enemies более консистентно и переиспользует логику
        
        # --- Инициализация других сущностей ---
        # TODO: Инициализация инвентаря, глобального состояния и т.д.


    def get_player_group(self) -> List['Player']:
        """Получить текущую группу игроков."""
        return self.player_group

    # TODO: Добавить методы для управления другими сущностями
    # def get_global_inventory(self) -> 'Inventory': ...
    # def start_new_battle(self, enemies: List['Monster']) -> None: ...
    # и т.д.


    def get_current_enemies(self) -> List['Monster']:
        """
        Получение списка текущих врагов (монстров) в бою.

        Returns:
            List[Monster]: Список объектов Monster, представляющих текущих врагов.
                           Если врагов нет, возвращается пустой список.
        """
        return self.current_enemies.copy() # Возвращаем копию, чтобы предотвратить случайное изменение внутреннего списка извне


    def create_enemies(self, enemy_data_list: List[Dict[str, Any]]) -> bool:
        """
        Создание новой группы врагов (монстров) и сохранение их в current_enemies.

        Args:
            enemy_data_list (List[Dict[str, Any]]): Список словарей с данными для создания монстров.
                Каждый словарь может содержать ключи:
                - 'role' (str, обязательный): Роль/тип монстра (например, 'goblin', 'dragon').
                - 'level' (int, опциональный): Уровень монстра. По умолчанию 1.
                - 'name' (str, опциональный): Имя монстра. Если не указано,
                                             будет сгенерировано фабрикой.

        Returns:
            bool: Монстры созданы.

        Example:
            enemy_data = [
                {'role': 'goblin', 'level': 2},
                {'role': 'orc', 'name': 'Громила'},
                {'role': 'dragon'} # Будет уровень 1
            ]
            new_enemies = game_manager.create_enemies(enemy_data)
        """
        # Очищаем список текущих врагов перед созданием новых
        self.current_enemies.clear()
        
        # Импортируем фабрику внутри метода, чтобы избежать циклических импортов
        from game.factories.monster_factory import create_monster

        for enemy_data in enemy_data_list:
            role = enemy_data.get('role')
            if not role:
                # Можно логировать ошибку или пропустить
                print(f"Предупреждение: Пропущен монстр без 'role': {enemy_data}")
                continue

            level = enemy_data.get('level', 1) # Уровень по умолчанию 1
            name = enemy_data.get('name') # Имя может быть None, тогда сгенерируется
            
            # Создаем монстра с помощью фабрики
            monster = create_monster(name=name, role=role, level=level)
            if monster:
                self.current_enemies.append(monster)
        
        return True # Возвращаем список только что созданных врагов

# Функция для удобного получения экземпляра GameManager
def get_game_manager() -> GameManager:
    """Получить глобальный экземпляр GameManager."""
    # Это гарантирует, что экземпляр будет создан при первом вызове
    return GameManager()
