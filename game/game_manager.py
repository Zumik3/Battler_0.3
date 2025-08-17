# game/game_manager.py
"""Менеджер игрового состояния."""

from typing import Any, Dict, List, Optional, TYPE_CHECKING
from game.config import get_config

if TYPE_CHECKING:
    from game.entities.player import Player
    from game.entities.monster import Monster

class GameManager:
    """Менеджер игрового состояния."""
    
    _instance: Optional['GameManager'] = None

    def __new__(cls) -> 'GameManager':
        """Реализация паттерна Singleton."""
        if cls._instance is None:
            cls._instance = super(GameManager, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Инициализирует менеджер игры и загружает начальное состояние."""
        if hasattr(self, 'initialized'):
            return

        self.config = get_config()
        self.player_group: List['Player'] = []
        self.current_enemies: List['Monster'] = []
        
        self._initialize_game_entities()
        self.initialized = True

    def _initialize_game_entities(self) -> None:
        """Создает и инициализирует стартовые сущности игры."""
        player_data_dir = self.config.system.player_classes_directory
        
        # Инициализация игроков
        starting_players = {
            "Роланд": "berserker",
            "Стайлс": "rogue", 
            "Морган": "mage",
            "Дамиан": "healer"
        }
        
        self._create_players(starting_players, player_data_dir)
        self._create_initial_enemies()

    def _create_players(self, player_data: Dict[str, str], data_dir: str) -> None:
        """Создает группу игроков."""
        from game.factories.player_factory import create_player
        
        for name, role in player_data.items():
            player = create_player(role=role, name=name, level=1, data_directory=data_dir)
            if player:
                self.player_group.append(player)

    def _create_initial_enemies(self) -> None:
        """Создает начальную группу врагов."""
        initial_enemy_data = [
            {'role': 'goblin', 'level': 1},
            {'role': 'orc', 'level': 2},
        ]
        self.create_enemies(initial_enemy_data)

    def get_player_group(self) -> List['Player']:
        """Получить текущую группу игроков."""
        return self.player_group.copy()

    def get_current_enemies(self) -> List['Monster']:
        """Получение списка текущих врагов."""
        return self.current_enemies.copy()

    def create_enemies(self, enemy_data_list: List[Dict[str, Any]]) -> bool:
        """Создание новой группы врагов."""
        self.current_enemies.clear()
        
        from game.factories.monster_factory import create_monster

        for enemy_data in enemy_data_list:
            role = enemy_data.get('role')
            if not role:
                # TODO: Заменить на логирование
                continue

            level = enemy_data.get('level', 1)
            name = enemy_data.get('name')
            
            monster = create_monster(name=name, role=role, level=level)
            if monster:
                self.current_enemies.append(monster)
        
        return True

def get_game_manager() -> GameManager:
    """Получить глобальный экземпляр GameManager."""
    return GameManager()