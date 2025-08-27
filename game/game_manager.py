# game/game_manager.py
"""Менеджер игрового состояния."""

from typing import Any, Dict, List, Optional, TYPE_CHECKING
from game.config import get_config
from game.core.game_context import ContextFactory
from game.systems.battle.manager import BattleManager
from game.rewards.handlers import register_reward_handlers
from game.systems.encounters.manager import EncounterManager

if TYPE_CHECKING:
    from game.entities.player import Player
    from game.entities.monster import Monster
    from game.core.game_context import GameContext

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
        self.context: 'GameContext' = ContextFactory.create_default_context(self.config)
        self.event_bus = self.context.event_bus
        self.battle_manager = BattleManager(self.context)
        self.encounter_manager = EncounterManager(self)
        self.player_group: List['Player'] = []
        self.current_enemies: List['Monster'] = []
        
        register_reward_handlers(self.context)

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
        
        self._create_players(
            player_data=starting_players, 
            data_dir=player_data_dir, 
            game_context=self.context)

        # TODO: сделать инициализацию при начале сражения/ивента
        # self._create_initial_enemies(
        #     game_context=self.context)

    def _create_players(self, player_data: Dict[str, str], data_dir: 
        str, game_context: 'GameContext') -> None:
        """Создает группу игроков."""
        from game.factories.player_factory import PlayerFactory
        
        for name, role in player_data.items():
            player = PlayerFactory.create_player(
                game_context=game_context,
                role=role,
                level=1
            )
            if player:
                self.player_group.append(player)

    def _create_initial_enemies(self, game_context: 'GameContext') -> None:
        """Создает начальную группу врагов."""
        initial_enemy_data = [
            {'role': 'goblin', 'level': 1},
            {'role': 'orc', 'level': 2},
        ]
        self.create_enemies(enemy_data_list=initial_enemy_data, game_context=game_context)

    def _start_battle(self, players: list['Player'], enemies: list['Monster']) -> None:
        """Запускает бой между командами.
        
        Args:
            players: Список персонажей игрока.
            enemies: Список врагов.
        """
        self.battle_manager.start_battle(players, enemies)

    def start_battle(self) -> None:
        self._start_battle(self.player_group, self.current_enemies)

    def get_player_group(self) -> List['Player']:
        """Получить текущую группу игроков."""
        return self.player_group.copy()

    def get_current_enemies(self) -> List['Monster']:
        """Получение списка текущих врагов."""
        return self.current_enemies.copy()

    def create_enemies(self, enemy_data_list: List[Dict[str, Any]], 
        game_context: 'GameContext') -> bool:
        """Создание новой группы врагов."""
        self.current_enemies.clear()
        
        from game.factories.monster_factory import MonsterFactory

        for enemy_data in enemy_data_list:
            role = enemy_data.get('role', 'goblin')
            level = enemy_data.get('level', 1)
            
            monster = MonsterFactory.create_monster(
                game_context=game_context,
                role=role, 
                level=level
            )
            if monster:
                self.current_enemies.append(monster)
        
        return True

def get_game_manager() -> GameManager:
    """Получить глобальный экземпляр GameManager."""
    return GameManager()