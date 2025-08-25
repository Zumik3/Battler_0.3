# game/ai/decision_makers/basic_enemy_ai.py
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
        Пока что это заглушка, которая возвращает случайное действие.
        """
        # TODO: Реализовать логику выбора действия
        # 1. Получить доступные способности через character.abilities.get_available_abilities()
        # 2. Выбрать одну из них
        # 3. Выбрать подходящую цель (или цели)
        # 4. Вернуть (имя_способности, [цель1, цель2, ...])
        
        # Пока возвращаем заглушку
        if enemies:
            return ("BasicAttack", [enemies[0]]) # Атакуем первого врага
        else:
            # Если врагов нет (теоретически), возвращаем пустое действие
            return ("BasicAttack", []) 