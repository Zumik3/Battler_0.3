# game/systems/encounters/room_generator.py
"""Генератор комнат для encounter'ей."""

import random
from typing import List, Dict, Any, Tuple
from game.systems.encounters.room import Room, BattleRoom, TreasureRoom, EmptyRoom, BossRoom, RoomType


class RoomGenerator:
    """Генератор комнат для последовательностей."""

    def __init__(self):
        """Инициализирует генератор комнат."""
        # Веса для выбора типов комнат
        self.room_type_weights = {
            RoomType.BATTLE: 60,
            RoomType.TREASURE: 20,
            RoomType.EMPTY: 15,
            RoomType.BOSS: 5  # Этот вес будет игнорироваться для обычных комнат
        }
        
        # Параметры для генерации врагов
        self.min_enemies_per_room = 1
        self.max_enemies_per_room = 4

    def generate_room(self, position: int, total_rooms: int, difficulty_level: int) -> Room:
        """
        Генерирует комнату для заданной позиции.
        
        Args:
            position: Позиция комнаты в последовательности
            total_rooms: Общее количество комнат
            difficulty_level: Уровень сложности (средний уровень группы)
            
        Returns:
            Сгенерированная комната
        """
        # Последняя комната всегда боссовая
        if position == total_rooms - 1:
            return self._generate_boss_room(position, total_rooms, difficulty_level)
        
        # Для первой комнаты всегда делаем боевую
        if position == 0:
            return self._generate_battle_room(position, total_rooms, difficulty_level)
        
        # Для остальных комнат выбираем тип случайным образом
        room_type = self._select_room_type(position, total_rooms)
        
        if room_type == RoomType.BATTLE:
            return self._generate_battle_room(position, total_rooms, difficulty_level)
        elif room_type == RoomType.TREASURE:
            return self._generate_treasure_room(position, total_rooms)
        elif room_type == RoomType.EMPTY:
            return self._generate_empty_room(position, total_rooms)
        else:
            # fallback на боевую комнату
            return self._generate_battle_room(position, total_rooms, difficulty_level)

    def _select_room_type(self, position: int, total_rooms: int) -> RoomType:
        """
        Выбирает тип комнаты на основе весов.
        
        Args:
            position: Позиция комнаты
            total_rooms: Общее количество комнат
            
        Returns:
            Тип выбранной комнаты
        """
        # Создаем список с учетом весов
        weighted_types = []
        for room_type, weight in self.room_type_weights.items():
            # Игнорируем BOSS для обычных комнат
            if room_type != RoomType.BOSS:
                weighted_types.extend([room_type] * weight)
        
        # Выбираем случайный тип
        return random.choice(weighted_types)

    def _generate_battle_room(self, position: int, total_rooms: int, difficulty_level: int) -> BattleRoom:
        """
        Генерирует боевую комнату.
        
        Args:
            position: Позиция комнаты
            total_rooms: Общее количество комнат
            difficulty_level: Уровень сложности
            
        Returns:
            Боевая комната
        """
        # Определяем количество врагов
        if position == 0:
            # Первая комната - небольшая группа врагов для разминки
            enemy_count = random.randint(1, 2)
        elif position == total_rooms - 1:
            # Боссовая комната - один сильный враг
            enemy_count = 1
        else:
            # Обычная комната - от 1 до 3 врагов
            enemy_count = random.randint(1, min(3, self.max_enemies_per_room))
        
        # Генерируем врагов
        enemies = self._generate_enemies(enemy_count, difficulty_level, position, total_rooms)
        
        return BattleRoom(position, total_rooms, enemies)

    def _generate_boss_room(self, position: int, total_rooms: int, difficulty_level: int) -> BossRoom:
        """
        Генерирует боссовую комнату.
        
        Args:
            position: Позиция комнаты
            total_rooms: Общее количество комнат
            difficulty_level: Уровень сложности
            
        Returns:
            Боссовая комната
        """
        # Босс всегда на 2-3 уровня выше группы
        boss_level = difficulty_level + random.randint(2, 3)
        
        # Выбираем тип босса
        boss_types = ["troll", "wizard"]
        boss_type = random.choice(boss_types)
        
        enemies = [
            {
                'role': boss_type,
                'level': boss_level
            }
        ]
        
        return BossRoom(position, total_rooms, enemies)

    def _generate_treasure_room(self, position: int, total_rooms: int) -> TreasureRoom:
        """
        Генерирует комнату с сокровищами.
        
        Args:
            position: Позиция комнаты
            total_rooms: Общее количество комнат
            
        Returns:
            Комната с сокровищами
        """
        # TODO: Реализовать генерацию реальных наград
        rewards = [
            {"type": "experience", "amount": 50},
            {"type": "gold", "amount": 25}
        ]
        
        return TreasureRoom(position, total_rooms, rewards)

    def _generate_empty_room(self, position: int, total_rooms: int) -> EmptyRoom:
        """
        Генерирует пустую комнату.
        
        Args:
            position: Позиция комнаты
            total_rooms: Общее количество комнат
            
        Returns:
            Пустая комната
        """
        return EmptyRoom(position, total_rooms)

    def _generate_enemies(self, count: int, difficulty_level: int, position: int, total_rooms: int) -> List[Dict[str, Any]]:
        """
        Генерирует список врагов.
        
        Args:
            count: Количество врагов
            difficulty_level: Уровень сложности
            position: Позиция комнаты
            total_rooms: Общее количество комнат
            
        Returns:
            Список врагов
        """
        enemies = []
        
        # Определяем уровни врагов
        enemy_levels = self._distribute_enemy_levels(count, difficulty_level, position, total_rooms)
        
        # Типы врагов по уровням
        enemy_types_by_level = {
            1: ["goblin", "skeleton"],
            2: ["goblin", "skeleton", "orc"],
            3: ["goblin", "skeleton", "orc"],
            4: ["skeleton", "orc"],
            5: ["skeleton", "orc", "wizard"],
            6: ["orc", "wizard"],
            7: ["orc", "wizard", "troll"],
            8: ["wizard", "troll"],
            9: ["wizard", "troll"],
            10: ["troll", "wizard"]
        }
        
        for level in enemy_levels:
            # Ограничиваем уровень в пределах доступных типов
            clamped_level = max(1, min(level, 10))
            
            # Выбираем доступные типы для этого уровня
            available_types = enemy_types_by_level.get(clamped_level, ["goblin"])
            
            # Выбираем случайный тип
            enemy_type = random.choice(available_types)
            
            enemies.append({
                'role': enemy_type,
                'level': level
            })
            
        return enemies

    def _distribute_enemy_levels(self, count: int, difficulty_level: int, position: int, total_rooms: int) -> List[int]:
        """
        Распределяет уровни между врагами.
        
        Args:
            count: Количество врагов
            difficulty_level: Уровень сложности
            position: Позиция комнаты
            total_rooms: Общее количество комнат
            
        Returns:
            Список уровней врагов
        """
        if count <= 0:
            return []
        
        # Для босса всегда один сильный враг
        if position == total_rooms - 1:
            boss_level = difficulty_level + random.randint(2, 3)
            return [boss_level]
        
        # Для обычных комнат распределяем уровни вокруг difficulty_level
        levels = []
        for _ in range(count):
            # Небольшое отклонение от среднего уровня
            deviation = random.randint(-1, 2)
            level = max(1, difficulty_level + deviation)
            levels.append(level)
            
        return levels

    def set_room_type_weights(self, weights: Dict[RoomType, int]) -> None:
        """
        Устанавливает веса для типов комнат.
        
        Args:
            weights: Словарь весов {RoomType: weight}
        """
        self.room_type_weights = weights

    def get_room_type_weights(self) -> Dict[RoomType, int]:
        """
        Возвращает текущие веса типов комнат.
        
        Returns:
            Словарь весов
        """
        return self.room_type_weights.copy()