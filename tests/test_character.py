# tests/test_character.py
"""Тесты для класса Character и его свойств."""

import pytest
from unittest.mock import Mock, patch

from game.entities.character import Character, CharacterConfig
from game.core.character_context import CharacterContext
from game.entities.player import Player
from game.factories.player_factory import PlayerConfig

# ==================== Фикстуры ====================

@pytest.fixture
def mock_event_bus():
    """Фикстура для мока шины событий."""
    return Mock()

@pytest.fixture
def player_config() -> PlayerConfig:
    """Фикстура с конфигом для создания игрока."""
    return PlayerConfig(
        name="TestPlayer",
        role="warrior",
        base_stats={
            'strength': 10,
            'agility': 10,
            'intelligence': 10,
            'vitality': 10
        },
        growth_rates={
            'strength': 1.0,
            'agility': 1.0,
            'intelligence': 1.0,
            'vitality': 1.0
        }
    )

@pytest.fixture
def character(player_config: PlayerConfig, mock_event_bus: Mock) -> Character:
    """Фикстура для создания экземпляра Character с моками."""
    mock_game_context = Mock()
    mock_game_context.event_bus = mock_event_bus

    char_context = CharacterContext(event_bus=mock_event_bus)

    with patch('game.factories.character_property_factory.CharacterPropertyFactory'), \
         patch('game.factories.player_property_factory.PlayerPropertyFactory'):
        char_instance = Player(context=char_context, game_context=mock_game_context, config=player_config)
        char_instance.health = Mock()
        char_instance.abilities = Mock()
        return char_instance

# ==================== Тесты ====================

class TestCharacterCreation:
    """Минимальные тесты для проверки создания персонажа."""

    def test_character_initialization(self, player_config: PlayerConfig, mock_event_bus: Mock):
        """Тест, что персонаж создается с базовыми атрибутами."""
        char_context = CharacterContext(event_bus=mock_event_bus)
        
        with patch('game.factories.character_property_factory.CharacterPropertyFactory'), \
             patch('game.factories.player_property_factory.PlayerPropertyFactory'):
            character = Player(context=char_context, game_context=Mock(), config=player_config)
            assert character.name == "TestPlayer"
            assert character.role == "warrior"
            assert character.is_player is True
            assert character.is_alive() is True

    def test_is_alive(self, character: Character):
        """Тест проверки состояния жизни персонажа."""
        assert character.is_alive() is True
        character.alive = False
        assert character.is_alive() is False

