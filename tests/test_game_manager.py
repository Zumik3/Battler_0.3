# tests/test_game_manager.py
"""Тесты для модуля game.game_manager, включая класс GameManager и функцию get_game_manager."""

import pytest
from unittest.mock import patch, MagicMock
from game.game_manager import GameManager, get_game_manager

class TestGameManager:
    """Тесты для класса GameManager."""

    def test_singleton_instance_via_get_game_manager(self) -> None:
        """
        Тест: Функция get_game_manager возвращает один и тот же экземпляр GameManager.
        Проверяет реализацию паттерна Singleton.
        """
        manager1 = get_game_manager()
        manager2 = get_game_manager()
        assert manager1 is manager2

    @patch('game.game_manager.get_config')
    def test_initialization_with_config(self, mock_get_config) -> None:
        """
        Тест: Инициализация GameManager корректно загружает конфигурацию.
        """
        # --- Ключевое исправление: Сброс Singleton перед тестом ---
        GameManager._instance = None

        # Настройка моков
        mock_config_instance = MagicMock()
        mock_get_config.return_value = mock_config_instance

        # Вызов тестируемой функциональности
        manager = get_game_manager()

        # Проверки
        mock_get_config.assert_called_once()

    def test_get_player_group(self) -> None:
        """
        Тест: Метод get_player_group возвращает список игроков.
        """
        manager = get_game_manager()

        # Создание мок-игроков и установка их в менеджер
        mock_player1 = MagicMock()
        mock_player2 = MagicMock()
        manager.player_group = [mock_player1, mock_player2]

        # Вызов тестируемой функциональности
        player_group = manager.get_player_group()

        # Проверки
        assert player_group == [mock_player1, mock_player2]
        assert len(player_group) == 2
