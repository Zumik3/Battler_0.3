# game/systems/encounters/encounter_generator.py
"""Система генерации encounter'ов на основе уровня группы игроков."""

from typing import List, Tuple, Dict, Any
import random
from game.entities.player import Player
from game.entities.monster import Monster
from game.systems.encounters.encounter import Encounter
from game.systems.encounters.enemy_factory import EnemyFactory
from game.systems.encounters.difficulty_scaling import DifficultyScaler


class EncounterGenerator:
    """Генератор encounter'ов на основе состава группы игроков."""

    def __init__(self):
        """Инициализирует генератор encounter'ов."""
        self.enemy_factory = EnemyFactory()
        self.difficulty_scaler = DifficultyScaler()

    def generate_encounter_for_group(self, player_group: List[Player]) -> Encounter:
        """
        Генерирует encounter на основе состава группы игроков.
        
        Args:
            player_group: Список игроков в группе
            
        Returns:
            Сгенерированный encounter
        """
        if not player_group:
            raise ValueError("Группа игроков не может быть пустой")

        # Рассчитываем параметры encounter
        min_level, max_level, avg_level = self._calculate_group_levels(player_group)
        enemy_min_level, enemy_max_level = self._calculate_enemy_level_range(min_level, max_level, avg_level)
        enemy_count = self.difficulty_scaler.calculate_enemy_count(avg_level)
        enemy_levels = self._distribute_enemy_levels(avg_level, enemy_min_level, enemy_max_level, enemy_count)
        enemy_types = self._select_enemy_types(enemy_levels)

        # Создаем врагов
        enemies_data = []
        for enemy_type, level in zip(enemy_types, enemy_levels):
            enemies_data.append({
                'role': enemy_type,
                'level': level
            })

        # Создаем encounter
        description = self._generate_encounter_description(enemy_count, avg_level)
        difficulty = self._determine_difficulty(avg_level)
        
        encounter = Encounter(
            name=f"Битва {avg_level} уровня",
            description=description,
            difficulty=difficulty,
            events=[]  # Будет заполнен позже
        )
        
        # Добавляем событие боя с созданными врагами
        from game.systems.encounters.events import BattleEncounterEvent
        battle_event = BattleEncounterEvent(enemies=enemies_data)
        encounter.events.append(battle_event)
        
        return encounter

    def _calculate_group_levels(self, player_group: List[Player]) -> Tuple[int, int, int]:
        """
        Рассчитывает минимальный, максимальный и средний уровни группы.
        
        Args:
            player_group: Список игроков
            
        Returns:
            Кортеж (min_level, max_level, avg_level)
        """
        levels = [player.level.get_level() for player in player_group]
        min_level = min(levels)
        max_level = max(levels)
        avg_level = round(sum(levels) / len(levels))
        return min_level, max_level, avg_level

    def _calculate_enemy_level_range(self, min_level: int, max_level: int, avg_level: int) -> Tuple[int, int]:
        """
        Рассчитывает диапазон уровней для врагов.
        
        Args:
            min_level: Минимальный уровень в группе
            max_level: Максимальный уровень в группе
            avg_level: Средний уровень группы
            
        Returns:
            Кортеж (enemy_min_level, enemy_max_level)
        """
        enemy_min_level = min_level
        enemy_max_level = min(max_level + 2, avg_level + 3)
        return enemy_min_level, enemy_max_level

    def _distribute_enemy_levels(self, avg_level: int, min_level: int, max_level: int, count: int) -> List[int]:
        """
        Распределяет уровни между врагами.
        
        Args:
            avg_level: Средний уровень группы
            min_level: Минимальный уровень врага
            max_level: Максимальный уровень врага
            count: Количество врагов
            
        Returns:
            Список уровней врагов
        """
        if count <= 0:
            return []

        enemy_levels = []
        for _ in range(count):
            # Используем нормальное распределение вокруг avg_level
            # но с ограничением min/max границами
            level = round(random.gauss(avg_level, 1))
            level = max(min_level, min(max_level, level))  # clamp
            enemy_levels.append(level)
            
        return enemy_levels

    def _select_enemy_types(self, enemy_levels: List[int]) -> List[str]:
        """
        Выбирает типы врагов в зависимости от их уровней.
        
        Args:
            enemy_levels: Список уровней врагов
            
        Returns:
            Список типов врагов
        """
        enemy_types = []
        for level in enemy_levels:
            available_types = self.enemy_factory.get_available_enemy_types(level)
            if available_types:
                # Выбираем случайный тип из доступных
                enemy_type = random.choice(available_types)
                enemy_types.append(enemy_type)
            else:
                # Если нет доступных типов, используем goblin по умолчанию
                enemy_types.append("goblin")
                
        return enemy_types

    def _generate_encounter_description(self, enemy_count: int, avg_level: int) -> str:
        """
        Генерирует описание encounter'а.
        
        Args:
            enemy_count: Количество врагов
            avg_level: Средний уровень группы
            
        Returns:
            Описание encounter'а
        """
        descriptions = [
            f"Вы столкнулись с группой из {enemy_count} врагов.",
            f"На вашем пути {enemy_count} противников {avg_level} уровня.",
            f"Внезапная встреча с {enemy_count} существами среднего уровня {avg_level}.",
            f"Бой с отрядом из {enemy_count} врагов, чей уровень соответствует {avg_level}."
        ]
        return random.choice(descriptions)

    def _determine_difficulty(self, avg_level: int) -> str:
        """
        Определяет сложность encounter'а на основе среднего уровня.
        
        Args:
            avg_level: Средний уровень группы
            
        Returns:
            Строка сложности ("Легко", "Средне", "Сложно")
        """
        if avg_level <= 2:
            return "Легко"
        elif avg_level <= 5:
            return "Средне"
        else:
            return "Сложно"