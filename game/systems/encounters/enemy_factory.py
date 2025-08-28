# game/systems/encounters/enemy_factory.py
"""Фабрика для создания врагов по заданным параметрам."""

from typing import List, Dict, Set
import random
from game.entities.monster import Monster


class EnemyFactory:
    """Фабрика для создания врагов с учетом их уровней и типов."""

    def __init__(self):
        """Инициализирует фабрику врагов."""
        # Определяем, какие типы врагов доступны на каких уровнях
        self.enemy_level_requirements: Dict[str, int] = {
            "goblin": 1,
            "skeleton": 1,
            "orc": 3,
            "wizard": 5,
            "troll": 8
        }
        
        # Веса для выбора типов врагов (чем выше вес, тем чаще появляется тип)
        self.enemy_type_weights: Dict[str, int] = {
            "goblin": 30,
            "skeleton": 25,
            "orc": 20,
            "wizard": 15,
            "troll": 10
        }

    def create_enemy(self, role: str, level: int) -> Monster:
        """
        Создает врага заданного типа и уровня.
        
        Args:
            role: Тип врага (goblin, orc, etc.)
            level: Уровень врага
            
        Returns:
            Созданный экземпляр Monster
            
        Raises:
            ValueError: Если тип врага не поддерживается
        """
        # В реальной реализации здесь будет создание врага через фабрику
        # Пока возвращаем заглушку
        from game.factories.monster_factory import MonsterFactory
        from game.core.game_context import ContextFactory
        
        # Создаем контекст (в реальной реализации будет передаваться извне)
        context = ContextFactory.create_default_context()
        
        try:
            monster = MonsterFactory.create_monster(
                game_context=context,
                role=role,
                level=level
            )
            return monster
        except ValueError:
            # Если тип не найден, создаем goblin по умолчанию
            return MonsterFactory.create_monster(
                game_context=context,
                role="goblin",
                level=level
            )

    def get_available_enemy_types(self, max_level: int) -> List[str]:
        """
        Возвращает список типов врагов, доступных для заданного уровня.
        
        Args:
            max_level: Максимальный уровень, на котором должны быть доступны враги
            
        Returns:
            Список доступных типов врагов
        """
        available_types = []
        for enemy_type, required_level in self.enemy_level_requirements.items():
            if required_level <= max_level:
                available_types.append(enemy_type)
        return available_types

    def select_enemy_type_for_level(self, level: int) -> str:
        """
        Выбирает тип врага с учетом весов и доступности на заданном уровне.
        
        Args:
            level: Уровень для которого выбирается враг
            
        Returns:
            Тип выбранного врага
        """
        available_types = self.get_available_enemy_types(level)
        if not available_types:
            return "goblin"  # По умолчанию
            
        # Формируем список с учетом весов
        weighted_types = []
        for enemy_type in available_types:
            weight = self.enemy_type_weights.get(enemy_type, 10)  # По умолчанию вес 10
            weighted_types.extend([enemy_type] * weight)
            
        # Выбираем случайный тип
        return random.choice(weighted_types)

    def get_enemy_level_requirements(self) -> Dict[str, int]:
        """
        Возвращает словарь с требованиями уровней для врагов.
        
        Returns:
            Словарь {тип_врага: минимальный_уровень}
        """
        return self.enemy_level_requirements.copy()

    def get_enemy_type_weights(self) -> Dict[str, int]:
        """
        Возвращает словарь с весами типов врагов.
        
        Returns:
            Словарь {тип_врага: вес}
        """
        return self.enemy_type_weights.copy()

    def set_enemy_level_requirement(self, enemy_type: str, level: int) -> None:
        """
        Устанавливает минимальный уровень для типа врага.
        
        Args:
            enemy_type: Тип врага
            level: Минимальный уровень
        """
        self.enemy_level_requirements[enemy_type] = level

    def set_enemy_type_weight(self, enemy_type: str, weight: int) -> None:
        """
        Устанавливает вес для типа врага.
        
        Args:
            enemy_type: Тип врага
            weight: Вес (чем выше, тем чаще появляется)
        """
        self.enemy_type_weights[enemy_type] = weight