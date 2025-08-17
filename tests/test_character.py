# tests/entities/test_character.py
"""Базовые тесты для класса Character."""

from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock
import pytest

from game.entities.character import Character, SimpleStats, SimpleAttributes, CharacterConfig
from game.results import ActionResult, DamageTakenResult, HealedResult


# ==================== Фикстуры ====================

@pytest.fixture
def character_config() -> CharacterConfig:
    """Фикстура с конфигом для создания персонажа."""
    return CharacterConfig(
        name="TestCharacter",
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
        },
        level=1
    )


@pytest.fixture
def mock_config() -> Mock:
    """Фикстура с моком конфига."""
    config = Mock()
    config.character.base_max_hp = 50
    config.character.hp_per_vitality = 5
    config.character.base_max_energy = 20
    config.character.energy_per_intelligence = 3
    config.character.attack_per_strength = 2
    config.character.defense_per_agility = 1.5
    return config


# ==================== Тесты ====================

class TestCharacterConfig:
    """Тесты для CharacterConfig."""

    def test_character_config_initialization(self, character_config: CharacterConfig):
        """Тест инициализации конфига персонажа."""
        assert character_config.name == "TestCharacter"
        assert character_config.role == "warrior"
        assert character_config.level == 1
        assert character_config.is_player is False
        assert character_config.base_stats['strength'] == 10
        assert character_config.growth_rates['agility'] == 1.0


class TestSimpleStats:
    """Тесты для SimpleStats."""

    def test_simple_stats_initialization(self):
        """Тест инициализации SimpleStats."""
        stats = SimpleStats()
        assert stats.strength == 0
        assert stats.agility == 0
        assert stats.intelligence == 0
        assert stats.vitality == 0

    def test_simple_stats_with_values(self):
        """Тест инициализации SimpleStats с заданными значениями."""
        stats = SimpleStats(strength=15, agility=12, intelligence=8, vitality=20)
        assert stats.strength == 15
        assert stats.agility == 12
        assert stats.intelligence == 8
        assert stats.vitality == 20


class TestSimpleAttributes:
    """Тесты для SimpleAttributes."""

    def test_simple_attributes_initialization(self):
        """Тест инициализации SimpleAttributes."""
        attributes = SimpleAttributes()
        assert attributes.max_hp == 0
        assert attributes.max_energy == 0
        assert attributes.attack_power == 0
        assert attributes.defense == 0

    @patch('game.entities.character.get_config')
    def test_simple_attributes_recalculate(self, mock_get_config, mock_config: Mock):
        """Тест пересчета атрибутов."""
        mock_get_config.return_value = mock_config
        
        stats = SimpleStats()
        stats.strength = 10
        stats.agility = 10
        stats.intelligence = 10
        stats.vitality = 10
        
        attributes = SimpleAttributes()
        attributes.recalculate(stats, mock_config)

        # Проверяем расчеты
        expected_max_hp = 50 + (10 * 5)  # base_max_hp + (vitality * hp_per_vitality)
        expected_max_energy = 20 + (10 * 3)  # base_max_energy + (intelligence * energy_per_intelligence)
        expected_attack_power = 10 * 2  # strength * attack_per_strength
        expected_defense = int(10 * 1.5)  # int(agility * defense_per_agility)

        assert attributes.max_hp == expected_max_hp
        assert attributes.max_energy == expected_max_energy
        assert attributes.attack_power == expected_attack_power
        assert attributes.defense == expected_defense


class TestCharacter:
    """Базовые тесты для Character."""

    @patch('game.entities.character.get_config')
    def test_character_initialization(self, mock_get_config, character_config: CharacterConfig, mock_config: Mock):
        """Тест инициализации персонажа."""
        mock_get_config.return_value = mock_config
        
        character = Character(character_config)

        assert character.name == "TestCharacter"
        assert character.role == "warrior"
        assert character.level == 1
        assert character.is_player is False
        assert character.alive is True
        assert hasattr(character, 'stats')
        assert hasattr(character, 'attributes')
        assert isinstance(character.stats, SimpleStats)
        assert isinstance(character.attributes, SimpleAttributes)

    @patch('game.entities.character.get_config')
    def test_character_initialization_with_factories(self, mock_get_config, mock_config: Mock):
        """Тест инициализации персонажа с кастомными фабриками."""
        mock_get_config.return_value = mock_config
        
        # Создаем кастомные фабрики
        def custom_stats_factory(role, level, base_stats, growth_rates):
            stats = SimpleStats()
            stats.strength = base_stats.get('strength', 0) + 5
            stats.agility = base_stats.get('agility', 0) + 5
            stats.intelligence = base_stats.get('intelligence', 0) + 5
            stats.vitality = base_stats.get('vitality', 0) + 5
            return stats

        def custom_attributes_factory(stats, config_obj):
            attributes = SimpleAttributes()
            attributes.max_hp = 200
            attributes.max_energy = 100
            attributes.attack_power = 50
            attributes.defense = 25
            return attributes

        config = CharacterConfig(
            name="CustomCharacter",
            role="mage",
            base_stats={'strength': 5, 'agility': 5, 'intelligence': 15, 'vitality': 8},
            growth_rates={'strength': 1.0, 'agility': 1.0, 'intelligence': 1.0, 'vitality': 1.0},
            stats_factory=custom_stats_factory,
            attributes_factory=custom_attributes_factory
        )

        character = Character(config)

        assert character.name == "CustomCharacter"
        assert character.stats.strength == 10  # 5 + 5
        assert character.attributes.max_hp == 200

    @patch('game.entities.character.get_config')
    def test_is_alive(self, mock_get_config, character_config: CharacterConfig, mock_config: Mock):
        """Тест проверки жив ли персонаж."""
        mock_get_config.return_value = mock_config
        
        character = Character(character_config)
            
        assert character.is_alive() is True
        character.alive = False
        assert character.is_alive() is False

    @patch('game.entities.character.get_config')
    def test_get_level(self, mock_get_config, character_config: CharacterConfig, mock_config: Mock):
        """Тест получения уровня персонажа."""
        mock_get_config.return_value = mock_config
        
        character = Character(character_config)
            
        assert character.get_level() == 1
        character.level = 5
        assert character.get_level() == 5

    @patch('game.entities.character.get_config')
    def test_level_up(self, mock_get_config, character_config: CharacterConfig, mock_config: Mock):
        """Тест повышения уровня персонажа."""
        mock_get_config.return_value = mock_config
        
        character = Character(character_config)
        initial_level = character.level
        initial_max_hp = character.attributes.max_hp

        results = character.level_up()

        assert character.level == initial_level + 1
        assert len(results) == 1
        assert isinstance(results[0], ActionResult)
        assert results[0].type == "level_up"
        # HP и энергия должны быть восстановлены до новых максимумов
        assert character.hp == character.attributes.max_hp
        assert character.energy == character.attributes.max_energy

    @patch('game.entities.character.get_config')
    def test_take_damage(self, mock_get_config, character_config: CharacterConfig, mock_config: Mock):
        """Тест получения урона."""
        mock_get_config.return_value = mock_config
        
        character = Character(character_config)
        character.attributes.defense = 4
        character.hp = 100
        initial_hp = character.hp

        # Урон 20, защита 4, фактический урон = max(1, 20 - 4//2) = 18
        results = character.take_damage(20)

        assert len(results) == 1
        assert isinstance(results[0], DamageTakenResult)
        assert results[0].damage == 18
        assert character.hp == initial_hp - 18
        assert character.alive is True

    @patch('game.entities.character.get_config')
    def test_take_damage_death(self, mock_get_config, character_config: CharacterConfig, mock_config: Mock):
        """Тест смерти персонажа от урона."""
        mock_get_config.return_value = mock_config
        
        character = Character(character_config)
        character.hp = 5
        character.attributes.defense = 0

        results = character.take_damage(10)

        assert len(results) >= 1
        assert character.hp == 0
        assert character.alive is False
        # Проверяем, что есть результат о смерти
        death_found = False
        for result in results:
            if hasattr(result, 'type') and result.type == "death":
                death_found = True
                break
        assert death_found is True

    @patch('game.entities.character.get_config')
    def test_take_heal(self, mock_get_config, character_config: CharacterConfig, mock_config: Mock):
        """Тест исцеления персонажа."""
        mock_get_config.return_value = mock_config
        
        character = Character(character_config)
        character.attributes.max_hp = 100
        character.hp = 50
        initial_hp = character.hp

        results = character.take_heal(30)

        assert len(results) == 1
        assert isinstance(results[0], HealedResult)
        assert results[0].heal_amount == 30
        assert character.hp == initial_hp + 30

    @patch('game.entities.character.get_config')
    def test_take_heal_over_max(self, mock_get_config, character_config: CharacterConfig, mock_config: Mock):
        """Тест исцеления выше максимального HP."""
        mock_get_config.return_value = mock_config
        
        character = Character(character_config)
        character.attributes.max_hp = 100
        character.hp = 90

        results = character.take_heal(20)

        assert results[0].heal_amount == 10  # Только 10 до максимума
        assert character.hp == 100

    @patch('game.entities.character.get_config')
    def test_restore_energy(self, mock_get_config, character_config: CharacterConfig, mock_config: Mock):
        """Тест восстановления энергии."""
        mock_get_config.return_value = mock_config
        
        character = Character(character_config)
        character.attributes.max_energy = 100
        character.energy = 50
        initial_energy = character.energy

        results = character.restore_energy(amount=30)

        assert len(results) == 1
        assert isinstance(results[0], ActionResult)
        assert results[0].type == "energy_restored"
        assert character.energy == initial_energy + 30

    @patch('game.entities.character.get_config')
    def test_restore_energy_over_max(self, mock_get_config, character_config: CharacterConfig, mock_config: Mock):
        """Тест восстановления энергии выше максимального значения."""
        mock_get_config.return_value = mock_config
        
        character = Character(character_config)
        character.attributes.max_energy = 100
        character.energy = 90

        results = character.restore_energy(amount=30)

        assert character.energy == 100  # Не должно превышать максимум

    @patch('game.entities.character.get_config')
    def test_spend_energy_success(self, mock_get_config, character_config: CharacterConfig, mock_config: Mock):
        """Тест успешной траты энергии."""
        mock_get_config.return_value = mock_config
        
        character = Character(character_config)
        character.energy = 50

        result = character.spend_energy(20)

        assert result is True
        assert character.energy == 30

    @patch('game.entities.character.get_config')
    def test_spend_energy_fail(self, mock_get_config, character_config: CharacterConfig, mock_config: Mock):
        """Тест неудачной траты энергии."""
        mock_get_config.return_value = mock_config
        
        character = Character(character_config)
        character.energy = 10

        result = character.spend_energy(20)

        assert result is False
        assert character.energy == 10  # Энергия не изменилась

    @patch('game.entities.character.get_config')
    def test_add_ability_without_manager(self, mock_get_config, character_config: CharacterConfig, mock_config: Mock):
        """Тест добавления способности без менеджера."""
        mock_get_config.return_value = mock_config
        
        character = Character(character_config)

        results = character.add_ability("test_ability", Mock())

        assert len(results) == 0  # Нет менеджера, результатов нет

    @patch('game.entities.character.get_config')
    def test_use_ability_without_manager(self, mock_get_config, character_config: CharacterConfig, mock_config: Mock):
        """Тест использования способности без менеджера."""
        mock_get_config.return_value = mock_config
        
        character = Character(character_config)

        results = character.use_ability("test_ability", [])

        assert len(results) == 0  # Нет менеджера, результатов нет

    @patch('game.entities.character.get_config')
    def test_add_status_effect_without_manager(self, mock_get_config, character_config: CharacterConfig, mock_config: Mock):
        """Тест добавления статус-эффекта без менеджера."""
        mock_get_config.return_value = mock_config
        
        character = Character(character_config)

        results = character.add_status_effect(Mock())

        assert len(results) == 0  # Нет менеджера, результатов нет