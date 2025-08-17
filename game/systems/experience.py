# game/systems/experience.py
"""Системы управления опытом и уровнями."""

from typing import List, TYPE_CHECKING
from game.protocols import (
    ExperienceCalculatorProtocol, 
    LevelUpHandlerProtocol,
    ExperienceSystemProtocol,
    LevelingSystemProtocol
)
from game.results import ActionResult, ExperienceGainedResult, LevelUpHealResult

if TYPE_CHECKING:
    from game.entities.character import Character

class ExperienceSystem(ExperienceSystemProtocol):
    """Система управления опытом персонажа."""
    
    def __init__(self, calculator: ExperienceCalculatorProtocol):
        self.calculator = calculator
    
    def calculate_exp_for_next_level(self, current_level: int) -> int:
        """Рассчитывает опыт для следующего уровня."""
        return self.calculator.calculate_exp_for_next_level(current_level)
    
    def add_experience(self, character: 'Character', amount: int) -> List[ExperienceGainedResult]:
        """Добавляет опыт персонажу."""
        results: List[ExperienceGainedResult] = []
        
        # Получаем текущий опыт персонажа
        current_exp = getattr(character, 'exp', 0)
        new_total_exp = current_exp + amount
        
        results.append(ExperienceGainedResult(
            character=character.name,
            exp_amount=amount,
            total_exp=new_total_exp
        ))
        
        return results

class LevelingSystem(LevelingSystemProtocol):
    """Система управления повышением уровней."""
    
    def __init__(self, handler: LevelUpHandlerProtocol):
        self.handler = handler
    
    def try_level_up(self, character: 'Character') -> List[ActionResult]:
        """Проверяет и выполняет повышение уровня."""
        results: List[ActionResult] = []
        
        # Вызываем родительский level_up если есть
        if hasattr(character, 'level_up'):
            character.level_up()
        
        # Дополнительная обработка
        handler_results = self.handler.handle_level_up(character)
        # Фильтруем только LevelUpHealResult (или преобразуем)
        for result in handler_results:
            if isinstance(result, LevelUpHealResult):
                results.append(result)
        
        return results