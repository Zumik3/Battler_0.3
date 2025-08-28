# game/systems/encounters/difficulty_scaling.py
"""Система масштабирования сложности encounter'ов."""

import random
from typing import Dict, Tuple


class DifficultyScaler:
    """Система для масштабирования сложности encounter'ов в зависимости от уровня."""

    def __init__(self):
        """Инициализирует систему масштабирования сложности."""
        # Параметры для расчета количества врагов
        self.enemy_count_params = {
            1: {"min": 2, "max": 2, "fixed": True},
            2: {"min": 2, "max": 3, "fixed": False},
            3: {"min": 2, "max": 3, "fixed": False},
            4: {"min": 2, "max": 4, "fixed": False},
            5: {"min": 2, "max": 4, "fixed": False},
            6: {"min": 2, "max": 4, "fixed": False},
            7: {"min": 3, "max": 4, "fixed": False},
            8: {"min": 3, "max": 4, "fixed": False},
            9: {"min": 3, "max": 4, "fixed": False},
            10: {"min": 3, "max": 5, "fixed": False, "high_chance": 0.7}
        }

    def calculate_enemy_count(self, avg_level: int) -> int:
        """
        Рассчитывает количество врагов на основе среднего уровня группы.
        
        Args:
            avg_level: Средний уровень группы игроков
            
        Returns:
            Количество врагов для encounter'а
        """
        # Ограничиваем уровень в пределах доступных параметров
        level = max(1, min(avg_level, 10))
        
        params = self.enemy_count_params.get(level, self.enemy_count_params[10])
        
        if params.get("fixed", False):
            # Фиксированное количество
            return params["min"]
        elif "high_chance" in params:
            # На 10 уровне чаще 5 врагов
            if random.random() < params["high_chance"]:
                return 5
            else:
                return random.randint(params["min"], 4)  # 3-4 врага
        else:
            # Случайное количество в диапазоне
            return random.randint(params["min"], params["max"])

    def get_level_distribution_weights(self, avg_level: int) -> Dict[int, float]:
        """
        Возвращает веса для распределения уровней врагов вокруг среднего уровня.
        
        Args:
            avg_level: Средний уровень группы
            
        Returns:
            Словарь {уровень: вес}
        """
        weights = {}
        # Создаем нормальное распределение вокруг avg_level
        for level_diff in range(-3, 4):  # от -3 до +3 от среднего уровня
            level = avg_level + level_diff
            if level < 1:
                continue
                
            # Веса по нормальному распределению (приблизительно)
            if level_diff == 0:
                weights[level] = 30  # Самый высокий вес для среднего уровня
            elif abs(level_diff) == 1:
                weights[level] = 20  # Высокий вес для ±1
            elif abs(level_diff) == 2:
                weights[level] = 10  # Средний вес для ±2
            else:
                weights[level] = 5   # Низкий вес для ±3
                
        return weights

    def adjust_for_group_composition(self, player_group) -> float:
        """
        Корректирует сложность encounter'а на основе состава группы.
        
        Args:
            player_group: Список игроков
            
        Returns:
            Коэффициент корректировки сложности (1.0 - нормальная сложность)
        """
        # TODO: Реализовать логику анализа состава группы
        # Например:
        # - Если много хилеров, увеличить количество врагов
        # - Если много кастеров, добавить врагов с сопротивлением магии
        # - Если один танк, добавить врагов, атакующих остальных
        
        # Пока возвращаем стандартную сложность
        return 1.0

    def get_scaling_parameters(self, avg_level: int) -> Dict[str, Any]:
        """
        Возвращает параметры масштабирования для заданного уровня.
        
        Args:
            avg_level: Средний уровень группы
            
        Returns:
            Словарь с параметрами масштабирования
        """
        level = max(1, min(avg_level, 10))
        return {
            "enemy_count": self.calculate_enemy_count(level),
            "level_variance": self._get_level_variance(level),
            "rarity_weights": self._get_rarity_weights(level)
        }

    def _get_level_variance(self, avg_level: int) -> int:
        """
        Возвращает вариативность уровней врагов.
        
        Args:
            avg_level: Средний уровень группы
            
        Returns:
            Максимальное отклонение уровня врагов от среднего
        """
        if avg_level <= 3:
            return 1
        elif avg_level <= 6:
            return 2
        else:
            return 3

    def _get_rarity_weights(self, avg_level: int) -> Dict[str, float]:
        """
        Возвращает веса редкости типов врагов.
        
        Args:
            avg_level: Средний уровень группы
            
        Returns:
            Словарь {редкость: вес}
        """
        if avg_level <= 3:
            return {"common": 70, "uncommon": 25, "rare": 5}
        elif avg_level <= 6:
            return {"common": 50, "uncommon": 35, "rare": 15}
        else:
            return {"common": 30, "uncommon": 40, "rare": 30}