# game/systems/implementations.py
"""Реализации различных протоколов."""

from typing import TYPE_CHECKING, List
from game.protocols import (
    ExperienceCalculatorProtocol, 
    LevelUpHandlerProtocol
)

from game.results import ActionResult, LevelUpHealResult
from game.config import GameConfig, get_config

if TYPE_CHECKING:
    from game.entities.character import Character

class SimpleExperienceCalculator(ExperienceCalculatorProtocol):
    """Простой калькулятор опыта для следующего уровня."""
    
    def __init__(self, game_config: 'GameConfig'):
        """
        Инициализация калькулятора опыта.

        Args:
            config: Объект конфигурации игры (GameConfig).
        """
        self.config = game_config

    def calculate_exp_for_next_level(self, current_level: int) -> int:
        """
        Рассчитывает опыт, необходимый для достижения следующего уровня.

        Args:
            current_level: Текущий уровень персонажа.

        Returns:
            Количество опыта, необходимое для следующего уровня.
        """
        return int(self.config.experience.formula_base * (current_level ** self.config.experience.formula_multiplier))

class SimpleLevelUpHandler(LevelUpHandlerProtocol):
    """Простой обработчик повышения уровня."""
    
    def handle_level_up(self, character: 'Character') -> List[ActionResult]:
        """Обработать повышение уровня и вернуть список результатов."""
        results: List[ActionResult] = []
        old_hp = character.hp
        character.hp = character.attributes.max_hp
        hp_restored = character.hp - old_hp
        
        old_energy = character.energy
        character.energy = character.attributes.max_energy
        energy_restored = character.energy - old_energy
        
        results.append(LevelUpHealResult(
            character=character.name,
            hp_restored=hp_restored,
            energy_restored=energy_restored
        ))
        
        return results