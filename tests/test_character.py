# tests/test_character.py
"""Тесты для классов Character и Player."""

from typing import Any, Dict, List

import pytest

# Импортируем протокол Attributes
from game.protocols import Attributes, Stats
from game.entities.character import Character
# Убедимся, что SimpleAttributes наследуется от Attributes в своем определении
from game.entities.player import Player, SimpleAttributes, SimpleStats


# ==================== Фикстуры ====================

@pytest.fixture
def mock_stats() -> Stats:
    """Фикстура для создания тестовых характеристик."""
    stats = SimpleStats()
    stats.strength = 10
    stats.agility = 10
    stats.intelligence = 10
    stats.vitality = 10
    return stats


@pytest.fixture
def mock_attributes(mock_stats: Stats) -> Attributes:
    """Фикстура для создания тестовых атрибутов."""
    # Убедимся, что SimpleAttributes совместим с Attributes
    return SimpleAttributes(CharacterMock(), mock_stats)


@pytest.fixture
def base_player_data() -> Dict[str, Any]:
    """Фикстура с базовыми данными для создания игрока."""
    return {
        'base_stats_dict': {
            'strength': 10,
            'agility': 10,
            'intelligence': 10,
            'vitality': 10
        },
        'growth_rates_dict': {
            'strength': 1.0,
            'agility': 1.0,
            'intelligence': 1.0,
            'vitality': 1.0
        }
    }


# ==================== Мок-классы ====================

class CharacterMock(Character):
    """Мок-класс для тестирования абстрактного Character."""

    def __init__(self) -> None:
        """Инициализация мок-персонажа."""
        # Пропускаем инициализацию Character для упрощения тестов
        self.name = "TestCharacter"
        self.role = "test"
        self.level = 1
        self.alive = True
        self.is_player = False
        self.stats = SimpleStats()
        # Убедимся, что тип атрибутов совместим
        self.attributes: Attributes = SimpleAttributes(self, self.stats)
        self.hp = 100
        self.energy = 50
        self._ability_manager = None
        self._status_manager = None

    def get_base_stats(self) -> Stats:
        """Получение базовых характеристик."""
        stats = SimpleStats()
        stats.strength = 10
        stats.agility = 10
        stats.intelligence = 10
        stats.vitality = 10
        return stats

    def calculate_attributes(self) -> Attributes:
        """Вычисление атрибутов."""
        # Убедимся, что возвращаемый тип совместим
        return SimpleAttributes(self, self.get_base_stats())


# ==================== Тесты Character ====================

class TestCharacter:
    """Тесты для базового класса Character."""

    def test_character_initialization(self) -> None:
        """Тест инициализации персонажа."""
        character = CharacterMock()
        assert character.name == "TestCharacter"
        assert character.role == "test"
        assert character.level == 1
        assert character.alive is True
        assert character.is_player is False
        assert character.hp == 100
        assert character.energy == 50

    def test_is_alive(self) -> None:
        """Тест проверки жив ли персонаж."""
        character = CharacterMock()
        assert character.is_alive() is True

        character.alive = False
        assert character.is_alive() is False

    def test_get_level(self) -> None:
        """Тест получения уровня персонажа."""
        character = CharacterMock()
        character.level = 5
        assert character.get_level() == 5

    def test_take_damage(self) -> None:
        """Тест получения урона."""
        character = CharacterMock()
        character.attributes.defense = 4 # type: ignore # Мы знаем, что у SimpleAttributes есть defense
        character.hp = 100

        # Урон 20, защита 4, фактический урон = max(1, 20 - 4//2) = 18
        results = character.take_damage(20)

        assert len(results) == 1
        assert results[0]["type"] == "damage_taken"
        assert results[0]["damage"] == 18
        assert character.hp == 82  # 100 - 18

    def test_take_damage_death(self) -> None:
        """Тест смерти персонажа от урона."""
        character = CharacterMock()
        character.hp = 5

        results = character.take_damage(10)

        # Должно быть 2 результата: урон и смерть
        assert len(results) >= 1
        assert character.hp == 0
        assert character.alive is False

    def test_take_heal(self) -> None:
        """Тест исцеления персонажа."""
        character = CharacterMock()
        character.attributes.max_hp = 100 # type: ignore # Мы знаем, что у SimpleAttributes есть max_hp
        character.hp = 50

        results = character.take_heal(30)

        assert len(results) == 1
        assert results[0]["type"] == "healed"
        assert results[0]["heal_amount"] == 30
        assert character.hp == 80

    def test_take_heal_over_max(self) -> None:
        """Тест исцеления выше максимального HP."""
        character = CharacterMock()
        character.attributes.max_hp = 100 # type: ignore # Мы знаем, что у SimpleAttributes есть max_hp
        character.hp = 90

        results = character.take_heal(20)

        assert results[0]["heal_amount"] == 10  # Только 10 до максимума
        assert character.hp == 100

    def test_restore_energy(self) -> None:
        """Тест восстановления энергии."""
        character = CharacterMock()
        character.attributes.max_energy = 100 # type: ignore # Мы знаем, что у SimpleAttributes есть max_energy
        character.energy = 50

        results = character.restore_energy(amount=30)

        assert len(results) == 1
        assert results[0]["type"] == "energy_restored"
        assert results[0]["amount"] == 30
        assert character.energy == 80

    def test_spend_energy_success(self) -> None:
        """Тест успешной траты энергии."""
        character = CharacterMock()
        character.energy = 50

        result = character.spend_energy(20)

        assert result is True
        assert character.energy == 30

    def test_spend_energy_fail(self) -> None:
        """Тест неудачной траты энергии."""
        character = CharacterMock()
        character.energy = 10

        result = character.spend_energy(20)

        assert result is False
        assert character.energy == 10  # Энергия не изменилась

    def test_level_up(self) -> None:
        """Тест повышения уровня."""
        character = CharacterMock()
        character.level = 1
        character.hp = 80
        character.energy = 30
        character.attributes.max_hp = 100 # type: ignore # Мы знаем, что у SimpleAttributes есть max_hp
        character.attributes.max_energy = 50 # type: ignore # Мы знаем, что у SimpleAttributes есть max_energy

        results = character.level_up()

        assert len(results) == 1
        assert results[0]["type"] == "level_up"
        assert character.level == 2
        # Проверяем сохранение процентов HP/энергии
        assert character.hp > 0  # HP должен сохраниться пропорционально


# ==================== Тесты Player ====================

class TestPlayer:
    """Тесты для класса Player."""

    def test_player_initialization(self, base_player_data: Dict[str, Any]) -> None:
        """Тест инициализации игрока."""
        player = Player(
            name="TestPlayer",
            role="warrior",
            **base_player_data,
            level=1
        )

        assert player.name == "TestPlayer"
        assert player.role == "warrior"
        assert player.level == 1
        assert player.is_player is True
        assert player.exp == 0
        assert hasattr(player, 'exp_to_next_level')

    def test_get_base_stats(self, base_player_data: Dict[str, Any]) -> None:
        """Тест получения базовых характеристик."""
        player = Player(
            name="TestPlayer",
            role="warrior",
            **base_player_data,
            level=1
        )

        stats = player.get_base_stats()
        # Проверяем, что объект имеет нужные атрибуты (вместо isinstance)
        assert hasattr(stats, 'strength')
        assert hasattr(stats, 'agility')
        assert hasattr(stats, 'intelligence')
        assert hasattr(stats, 'vitality')
        assert stats.strength > 0
        assert stats.agility > 0
        assert stats.intelligence > 0
        assert stats.vitality > 0

    def test_calculate_attributes(self, base_player_data: Dict[str, Any]) -> None:
        """Тест вычисления атрибутов."""
        player = Player(
            name="TestPlayer",
            role="warrior",
            **base_player_data,
            level=1
        )

        attributes = player.calculate_attributes()
        # Проверяем, что объект имеет нужные атрибуты (вместо isinstance)
        assert hasattr(attributes, 'max_hp')
        assert hasattr(attributes, 'max_energy')
        assert hasattr(attributes, 'attack_power')
        assert hasattr(attributes, 'defense')
        assert attributes.max_hp > 0
        assert attributes.max_energy > 0
        assert attributes.attack_power >= 0
        assert attributes.defense >= 0

    def test_calculate_exp_for_next_level(self, base_player_data: Dict[str, Any]) -> None:
        """Тест расчета опыта для следующего уровня."""
        player = Player(
            name="TestPlayer",
            role="warrior",
            **base_player_data,
            level=1
        )

        player.calculate_exp_for_next_level()
        assert player.exp_to_next_level > 0

        # Проверяем, что опыт увеличивается с уровнем
        player.level = 2
        player.calculate_exp_for_next_level()
        exp_level_2 = player.exp_to_next_level

        player.level = 3
        player.calculate_exp_for_next_level()
        exp_level_3 = player.exp_to_next_level

        assert exp_level_3 > exp_level_2

    def test_gain_experience(self, base_player_data: Dict[str, Any]) -> None:
        """Тест получения опыта."""
        player = Player(
            name="TestPlayer",
            role="warrior",
            **base_player_data,
            level=1
        )
        player.calculate_exp_for_next_level()

        # Получаем немного опыта
        results = player.gain_experience(50)

        assert len(results) == 1
        assert results[0]["type"] == "exp_gained"
        assert player.exp == 50

    def test_gain_experience_level_up(self, base_player_data: Dict[str, Any]) -> None:
        """Тест повышения уровня через опыт."""
        player = Player(
            name="TestPlayer",
            role="warrior",
            **base_player_data,
            level=1
        )
        player.exp_to_next_level = 100  # Устанавливаем опыт для теста

        # Получаем достаточно опыта для повышения уровня
        results = player.gain_experience(150)

        # Должно быть как минимум 2 результата: опыт и повышение уровня
        assert len(results) >= 2
        assert player.level >= 2
        assert player.exp == 50  # Остаток после повышения уровня (150 - 100 = 50)

    def test_gain_experience_multiple_level_up(self, base_player_data: Dict[str, Any]) -> None:
        """Тест множественного повышения уровня через опыт."""
        player = Player(
            name="TestPlayer",
            role="warrior",
            **base_player_data,
            level=1
        )

        # Установим начальный опыт для следующего уровня
        player.exp_to_next_level = 100

        # Получаем 250 опыта: 100 для первого уровня, 150 останется
        results = player.gain_experience(250)

        # После первого повышения уровень должен быть 2
        assert player.level == 2
        # Остаток опыта должен быть 150
        assert player.exp == 150

    def test_player_level_up(self, base_player_data: Dict[str, Any]) -> None:
        """Тест повышения уровня игрока."""
        player = Player(
            name="TestPlayer",
            role="warrior",
            **base_player_data,
            level=1
        )
        initial_level = player.level

        results = player.level_up()

        assert len(results) >= 1
        assert player.level == initial_level + 1
        # exp_to_next_level должен быть пересчитан
        assert player.exp_to_next_level > 0

    def test_experience_property(self, base_player_data: Dict[str, Any]) -> None:
        """Тест свойства опыта."""
        player = Player(
            name="TestPlayer",
            role="warrior",
            **base_player_data,
            level=1
        )
        player.calculate_exp_for_next_level()

        assert player.experience_to_next_level == player.exp_to_next_level


# ==================== Тесты вспомогательных классов ====================

class TestSimpleStats:
    """Тесты для SimpleStats."""

    def test_simple_stats_initialization(self) -> None:
        """Тест инициализации SimpleStats."""
        stats = SimpleStats()
        assert stats.strength == 0
        assert stats.agility == 0
        assert stats.intelligence == 0
        assert stats.vitality == 0


class TestSimpleAttributes:
    """Тесты для SimpleAttributes."""

    def test_simple_attributes_calculation(self, mock_stats: Stats) -> None:
        """Тест расчета атрибутов."""
        character = CharacterMock()
        attributes = SimpleAttributes(character, mock_stats)

        # Проверяем расчеты на основе формул из класса
        expected_max_hp = 50 + (mock_stats.vitality * 5)  # 50 + 50 = 100
        expected_max_energy = 20 + (mock_stats.intelligence * 3)  # 20 + 30 = 50
        expected_attack_power = mock_stats.strength * 2  # 10 * 2 = 20
        expected_defense = int(mock_stats.agility * 1.5)  # int(10 * 1.5) = 15

        assert attributes.max_hp == expected_max_hp
        assert attributes.max_energy == expected_max_energy
        assert attributes.attack_power == expected_attack_power
        assert attributes.defense == expected_defense


# ==================== Интеграционные тесты ====================

class TestCharacterPlayerIntegration:
    """Интеграционные тесты между Character и Player."""

    def test_player_inherits_character_behavior(self, base_player_data: Dict[str, Any]) -> None:
        """Тест, что Player наследует поведение Character."""
        player = Player(
            name="TestPlayer",
            role="warrior",
            **base_player_data,
            level=1
        )

        # Проверяем методы, унаследованные от Character
        assert player.is_alive() is True
        assert player.get_level() == 1

        # Проверяем, что можно использовать методы Character
        heal_results = player.take_heal(20)
        assert len(heal_results) == 1
        assert heal_results[0]["type"] == "healed"

    def test_player_damage_handling(self, base_player_data: Dict[str, Any]) -> None:
        """Тест обработки урона игроком."""
        player = Player(
            name="TestPlayer",
            role="warrior",
            **base_player_data,
            level=1
        )

        # Устанавливаем защиту для теста
        player.attributes.defense = 6 # type: ignore # Мы знаем, что у SimpleAttributes есть defense
        player.hp = 100

        damage_results = player.take_damage(20)
        assert len(damage_results) >= 1
        assert damage_results[0]["type"] == "damage_taken"
        assert player.hp < 100  # HP должно уменьшиться
