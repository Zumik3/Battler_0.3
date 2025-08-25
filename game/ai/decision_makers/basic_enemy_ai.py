# game/ai/decision_makers/basic_enemy_ai.py
import random
from typing import TYPE_CHECKING, List, Sequence, Tuple
from game.ai.ai_decision_maker import AIDecisionMaker

if TYPE_CHECKING:
    from game.entities.character import Character

class BasicEnemyAI(AIDecisionMaker):
    """Простая реализация ИИ для врагов."""
    
    def choose_action(
        self, 
        character: 'Character', 
        allies: Sequence['Character'], 
        enemies: Sequence['Character']
    ) -> Tuple[str, List['Character']]:
        """
        Выбирает действие для врага.
        """
        available_abilities: List[str] = []
        if character.abilities:
            available_abilities = character.abilities.get_available_abilities()
        
        chosen_ability = random.choice(available_abilities)
        target = random.choice(enemies)

        return (chosen_ability, [target])