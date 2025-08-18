# game/properties/level.py
"""Свойство уровня персонажа."""

from dataclasses import dataclass
from typing import List
from game.results import ActionResult
from game.events.character import LevelUpEvent

@dataclass
class LevelProperty:
    """Свойство для управления уровнем персонажа."""
    
    level: int = 1
    
    def level_up(self) -> List[ActionResult]:
        """Повышает уровень персонажа."""
        old_level = self.level
        self.level += 1
        
        # Здесь можно публиковать событие через контекст
        event_bus.publish(LevelUpEvent(...))
        
        return [ActionResult(
            type="level_up",
            message=f"Уровень повышен с {old_level} до {self.level}!"
        )]
    
    def get_level(self) -> int:
        """Возвращает текущий уровень."""
        return self.level