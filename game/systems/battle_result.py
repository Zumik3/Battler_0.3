# game/systems/battle_result.py
"""Результаты завершенного боя."""

from dataclasses import dataclass
from typing import List, Optional
from game.entities.character import Character

@dataclass
class BattleResult:
    """
    Результаты завершенного боя.

    Атрибуты:
        players (List[Character]): Список игроков, участвовавших в бою.
        enemies (List[Character]): Список врагов, участвовавших в бою.
        alive_players (List[Character]): Список игроков, выживших после боя.
        dead_enemies (List[Character]): Список врагов, побежденных в бою.
        battle_log (List[str]): (Опционально) Лог боя.
        battle_id (Optional[str]): (Опционально) Уникальный идентификатор боя.
    """
    players: List[Character]
    enemies: List[Character]
    alive_players: List[Character]
    dead_enemies: List[Character]
    battle_log: Optional[List[str]] = None
    battle_id: Optional[str] = None

    def __post_init__(self):
        """Пост-инициализация для валидации."""
        # Можно добавить проверки, например:
        # - Все alive_players должны быть в players
        # - Все dead_enemies должны быть в enemies
        # - alive_players не должны быть мертвы (is_alive() == False для dead_enemies)
        # Пока оставим базовую структуру
        pass