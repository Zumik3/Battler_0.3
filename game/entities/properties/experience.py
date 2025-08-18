# game/entities/components/experience.py
"""Свойство опыта персонажа."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from game.protocols import ExperienceSystemProtocol
    from game.results import ActionResult, ExperienceGainedResult

@dataclass
class ExperienceProperty(ExperienceSystemProtocol):
    """Свойство для управления здоровьем персонажа."""
    
    exp_to_level: int
    current_exp: int
    
    def __post_init__(self):
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
    
    def add_experience(self, amount: int) -> List['ExperienceGainedResult']:
        """Наносит урон, учитывая защиту."""
        results: List[ExperienceGainedResult] = []
        
        self.current_exp += amount

        results.append(ExperienceGainedResult(
            exp_amount=amount,
            total_exp=self.current_exp
        ))
        
        return results