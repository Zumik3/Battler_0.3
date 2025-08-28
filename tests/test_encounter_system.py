# tests/test_encounter_system.py
"""Тесты для системы генерации encounter'ов."""

import pytest
from unittest.mock import Mock, patch
from game.systems.encounters.encounter_generator import EncounterGenerator
from game.systems.encounters.enemy_factory import EnemyFactory
from game.systems.encounters.difficulty_scaling import DifficultyScaler
from game.entities.player import Player
from game.entities.monster import Monster


class TestEncounterGenerator:
    """Тесты для EncounterGenerator."""

    def test_init(self):
        """Тест инициализации EncounterGenerator."""
        generator = EncounterGenerator()
        assert generator.enemy_factory is not None
        assert generator.difficulty_scaler is not None

    def test_calculate_group_levels(self):
        """Тест расчета уровней группы."""
        generator = EncounterGenerator()
        
        # Создаем мок-игроков с разными уровнями
        player1 = Mock()
        player1.level.level = 1
        player2 = Mock()
        player2.level.level = 3
        player3 = Mock()
        player3.level.level = 2
        
        player_group = [player1, player2, player3]
        min_level, max_level, avg_level = generator._calculate_group_levels(player_group)
        
        assert min_level == 1
        assert max_level == 3
        assert avg_level == 2  # (1+3+2)/3 = 2

    def test_calculate_enemy_level_range(self):
        """Тест расчета диапазона уровней врагов."""
        generator = EncounterGenerator()
        
        # Тест с нормальными значениями
        enemy_min, enemy_max = generator._calculate_enemy_level_range(1, 3, 2)
        assert enemy_min == 1
        assert enemy_max == 5  # min(3+2, 2+3) = min(5, 5) = 5
        
        # Тест с ограничением по среднему уровню
        enemy_min, enemy_max = generator._calculate_enemy_level_range(1, 10, 2)
        assert enemy_min == 1
        assert enemy_max == 5  # min(10+2, 2+3) = min(12, 5) = 5

    def test_distribute_enemy_levels(self):
        """Тест распределения уровней врагов."""
        generator = EncounterGenerator()
        
        # Тест с 3 врагами
        levels = generator._distribute_enemy_levels(2, 1, 5, 3)
        assert len(levels) == 3
        # Проверяем, что все уровни в допустимом диапазоне
        for level in levels:
            assert 1 <= level <= 5


class TestEnemyFactory:
    """Тесты для EnemyFactory."""

    def test_init(self):
        """Тест инициализации EnemyFactory."""
        factory = EnemyFactory()
        assert "goblin" in factory.enemy_level_requirements
        assert "orc" in factory.enemy_level_requirements
        assert "troll" in factory.enemy_level_requirements

    def test_get_available_enemy_types(self):
        """Тест получения доступных типов врагов."""
        factory = EnemyFactory()
        
        # На 1 уровне доступны только goblin и skeleton
        available = factory.get_available_enemy_types(1)
        assert "goblin" in available
        assert "skeleton" in available
        assert "orc" not in available
        
        # На 5 уровне доступны все типы кроме troll
        available = factory.get_available_enemy_types(5)
        assert "goblin" in available
        assert "skeleton" in available
        assert "orc" in available
        assert "wizard" in available
        assert "troll" not in available
        
        # На 8 уровне доступны все типы
        available = factory.get_available_enemy_types(8)
        assert "goblin" in available
        assert "skeleton" in available
        assert "orc" in available
        assert "wizard" in available
        assert "troll" in available

    def test_select_enemy_type_for_level(self):
        """Тест выбора типа врага для уровня."""
        factory = EnemyFactory()
        
        # На 1 уровне должны выбираться только goblin или skeleton
        enemy_type = factory.select_enemy_type_for_level(1)
        assert enemy_type in ["goblin", "skeleton"]


class TestDifficultyScaler:
    """Тесты для DifficultyScaler."""

    def test_init(self):
        """Тест инициализации DifficultyScaler."""
        scaler = DifficultyScaler()
        assert scaler.enemy_count_params is not None

    def test_calculate_enemy_count(self):
        """Тест расчета количества врагов."""
        scaler = DifficultyScaler()
        
        # На 1 уровне всегда 2 врага
        count = scaler.calculate_enemy_count(1)
        assert count == 2
        
        # На 10 уровне от 3 до 5 врагов
        counts = [scaler.calculate_enemy_count(10) for _ in range(20)]
        for count in counts:
            assert 3 <= count <= 5

    def test_get_level_distribution_weights(self):
        """Тест получения весов распределения уровней."""
        scaler = DifficultyScaler()
        
        weights = scaler.get_level_distribution_weights(5)
        assert 5 in weights  # Средний уровень должен быть в весах
        assert weights[5] == 30  # Самый высокий вес для среднего уровня


if __name__ == "__main__":
    pytest.main([__file__])