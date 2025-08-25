# game/ai/base.py (псевдокод для понимания структуры)
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Sequence, Tuple

if TYPE_CHECKING:
    from game.entities.character import Character
    # Предполагаемые типы, могут быть другими
    from game.actions.action import Action 

class AIDecisionMaker(ABC):
    """Базовый класс для всех систем принятия решений ИИ."""

    @abstractmethod
    def choose_action(
        self, 
        character: 'Character', 
        allies: Sequence['Character'], 
        enemies: Sequence['Character']
    ) -> Tuple[str, List['Character']]: # (ability_name, targets)
        """
        Выбирает действие для персонажа на основе текущего состояния боя.

        Args:
            character: Персонаж, который должен принять решение.
            allies: Список живых союзников (включая самого персонажа для простоты или нет).
            enemies: Список живых врагов.

        Returns:
            Кортеж (имя_способности, список_целей).
        """
        pass
