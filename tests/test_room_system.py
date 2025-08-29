# tests/test_room_system.py
"""Тесты для системы комнат и последовательностей."""

import pytest
import random
from unittest.mock import Mock, patch
from game.systems.encounters.room import Room, BattleRoom, TreasureRoom, EmptyRoom, BossRoom, RoomType, RoomStatus
from game.systems.encounters.room_generator import RoomGenerator
from game.systems.encounters.room_sequence import RoomSequence, RoomSequenceProgress


class TestRoom:
    """Тесты для базового класса Room."""

    def test_room_initialization(self):
        """Тест инициализации комнаты."""
        room = Room(RoomType.BATTLE, 0, 5)
        assert room.room_type == RoomType.BATTLE
        assert room.position == 0
        assert room.total_rooms == 5
        assert room.status == RoomStatus.UNVISITED

    def test_room_status_changes(self):
        """Тест изменения статуса комнаты."""
        room = Room(RoomType.BATTLE, 0, 5)
        
        # Проверяем начальный статус
        assert room.status == RoomStatus.UNVISITED
        
        # Активируем комнату
        room.activate()
        assert room.status == RoomStatus.ACTIVE
        
        # Помечаем как пройденную
        room.complete()
        assert room.status == RoomStatus.COMPLETED
        
        # Помечаем как проваленную
        room.fail()
        assert room.status == RoomStatus.FAILED

    def test_boss_room_detection(self):
        """Тест определения боссовой комнаты."""
        # Обычная комната
        normal_room = Room(RoomType.BATTLE, 0, 5)
        assert not normal_room.is_boss_room()
        
        # Боссовая комната (последняя)
        boss_room = Room(RoomType.BOSS, 4, 5)
        assert boss_room.is_boss_room()


class TestBattleRoom:
    """Тесты для боевой комнаты."""

    def test_battle_room_initialization(self):
        """Тест инициализации боевой комнаты."""
        enemies = [{'role': 'goblin', 'level': 1}]
        room = BattleRoom(0, 5, enemies)
        
        assert room.room_type == RoomType.BATTLE
        assert room.enemies == enemies
        assert "бой" in room.description.lower()

    def test_battle_room_enter(self):
        """Тест входа в боевую комнату."""
        enemies = [{'role': 'goblin', 'level': 1}]
        room = BattleRoom(0, 5, enemies)
        
        result = room.enter()
        assert result["type"] == "battle"
        assert result["enemies"] == enemies


class TestTreasureRoom:
    """Тесты для комнаты с сокровищами."""

    def test_treasure_room_initialization(self):
        """Тест инициализации комнаты с сокровищами."""
        rewards = [{"type": "gold", "amount": 100}]
        room = TreasureRoom(1, 5, rewards)
        
        assert room.room_type == RoomType.TREASURE
        assert room.rewards == rewards
        assert "сокровищ" in room.description.lower()

    def test_treasure_room_enter(self):
        """Тест входа в комнату с сокровищами."""
        rewards = [{"type": "gold", "amount": 100}]
        room = TreasureRoom(1, 5, rewards)
        
        result = room.enter()
        assert result["type"] == "treasure"
        assert result["rewards"] == rewards


class TestEmptyRoom:
    """Тесты для пустой комнаты."""

    def test_empty_room_initialization(self):
        """Тест инициализации пустой комнаты."""
        room = EmptyRoom(2, 5)
        
        assert room.room_type == RoomType.EMPTY
        assert "пуст" in room.description.lower()

    def test_empty_room_enter(self):
        """Тест входа в пустую комнату."""
        room = EmptyRoom(2, 5)
        
        result = room.enter()
        assert result["type"] == "empty"


class TestBossRoom:
    """Тесты для боссовой комнаты."""

    def test_boss_room_initialization(self):
        """Тест инициализации боссовой комнаты."""
        enemies = [{'role': 'troll', 'level': 5}]
        room = BossRoom(4, 5, enemies)
        
        assert room.room_type == RoomType.BOSS
        assert room.enemies == enemies
        assert "босс" in room.description.lower()


class TestRoomSequenceProgress:
    """Тесты для отслеживания прогресса последовательности комнат."""

    def test_progress_initialization(self):
        """Тест инициализации прогресса."""
        progress = RoomSequenceProgress(5)
        
        assert progress.total_rooms == 5
        assert progress.completed_rooms == 0
        assert progress.current_room_index == -1

    def test_start_sequence(self):
        """Тест начала последовательности."""
        progress = RoomSequenceProgress(5)
        progress.start_sequence()
        
        assert progress.current_room_index == 0

    def test_complete_current_room(self):
        """Тест завершения текущей комнаты."""
        progress = RoomSequenceProgress(5)
        progress.start_sequence()
        progress.complete_current_room()
        
        assert progress.completed_rooms == 1

    def test_advance_to_next_room(self):
        """Тест перехода к следующей комнате."""
        progress = RoomSequenceProgress(5)
        progress.start_sequence()
        
        # Переход от комнаты 0 к комнате 1
        result = progress.advance_to_next_room()
        assert result
        assert progress.current_room_index == 1
        
        # Переход к последней комнате
        progress.current_room_index = 3
        result = progress.advance_to_next_room()
        assert result
        assert progress.current_room_index == 4
        
        # Попытка перехода за пределы последней комнаты
        result = progress.advance_to_next_room()
        assert not result

    def test_is_completed(self):
        """Тест проверки завершения последовательности."""
        progress = RoomSequenceProgress(3)
        
        # Не завершено
        assert not progress.is_completed()
        
        # Завершено
        progress.completed_rooms = 3
        assert progress.is_completed()

    def test_get_progress_info(self):
        """Тест получения информации о прогрессе."""
        progress = RoomSequenceProgress(5)
        progress.start_sequence()
        progress.completed_rooms = 2
        
        info = progress.get_progress_info()
        assert info["total_rooms"] == 5
        assert info["completed_rooms"] == 2
        assert info["current_room_index"] == 0
        assert info["progress_percentage"] == 40.0
        assert not info["is_completed"]


class TestRoomSequence:
    """Тесты для последовательности комнат."""

    def test_sequence_initialization(self):
        """Тест инициализации последовательности."""
        rooms = [Mock(), Mock(), Mock()]
        sequence = RoomSequence(rooms)
        
        assert sequence.rooms == rooms
        assert sequence.get_total_rooms() == 3
        assert sequence.get_completed_rooms_count() == 0

    def test_start_sequence(self):
        """Тест начала последовательности."""
        rooms = [Mock(), Mock(), Mock()]
        sequence = RoomSequence(rooms)
        
        first_room = sequence.start()
        assert first_room == rooms[0]
        assert sequence.progress.current_room_index == 0

    def test_get_current_room(self):
        """Тест получения текущей комнаты."""
        room1, room2, room3 = Mock(), Mock(), Mock()
        rooms = [room1, room2, room3]
        sequence = RoomSequence(rooms)
        
        # До начала последовательности
        assert sequence.get_current_room() is None
        
        # После начала
        sequence.start()
        assert sequence.get_current_room() == room1

    def test_complete_current_room(self):
        """Тест завершения текущей комнаты."""
        room1, room2 = Mock(), Mock()
        rooms = [room1, room2]
        sequence = RoomSequence(rooms)
        
        sequence.start()
        sequence.complete_current_room()
        
        assert sequence.get_completed_rooms_count() == 1
        room1.complete.assert_called_once()

    def test_advance_to_next_room(self):
        """Тест перехода к следующей комнате."""
        room1, room2, room3 = Mock(), Mock(), Mock()
        rooms = [room1, room2, room3]
        sequence = RoomSequence(rooms)
        
        sequence.start()
        next_room = sequence.advance_to_next_room()
        
        assert next_room == room2
        assert sequence.get_current_room() == room2

    def test_is_completed(self):
        """Тест проверки завершения последовательности."""
        room1, room2 = Mock(), Mock()
        rooms = [room1, room2]
        sequence = RoomSequence(rooms)
        
        # Не завершено
        assert not sequence.is_completed()
        
        # Завершено
        sequence.progress.completed_rooms = 2
        assert sequence.is_completed()

    def test_get_progress_info(self):
        """Тест получения информации о прогрессе последовательности."""
        room1, room2 = Mock(), Mock()
        room1.get_progress_info.return_value = {"position": 0, "status": "active"}
        rooms = [room1, room2]
        sequence = RoomSequence(rooms)
        sequence.set_name("Тестовая последовательность")
        sequence.set_description("Описание теста")
        
        sequence.start()
        info = sequence.get_progress_info()
        
        assert info["sequence_name"] == "Тестовая последовательность"
        assert info["sequence_description"] == "Описание теста"
        assert "current_room" in info


class TestRoomGenerator:
    """Тесты для генератора комнат."""

    def test_generator_initialization(self):
        """Тест инициализации генератора."""
        generator = RoomGenerator()
        assert generator.room_type_weights is not None

    def test_generate_battle_room(self):
        """Тест генерации боевой комнаты."""
        generator = RoomGenerator()
        room = generator._generate_battle_room(0, 5, 3)
        
        assert isinstance(room, BattleRoom)
        assert room.position == 0
        assert room.total_rooms == 5

    def test_generate_boss_room(self):
        """Тест генерации боссовой комнаты."""
        generator = RoomGenerator()
        room = generator._generate_boss_room(4, 5, 3)
        
        assert isinstance(room, BossRoom)
        assert room.position == 4
        assert room.total_rooms == 5

    def test_generate_treasure_room(self):
        """Тест генерации комнаты с сокровищами."""
        generator = RoomGenerator()
        room = generator._generate_treasure_room(1, 5)
        
        assert isinstance(room, TreasureRoom)
        assert room.position == 1
        assert room.total_rooms == 5

    def test_generate_empty_room(self):
        """Тест генерации пустой комнаты."""
        generator = RoomGenerator()
        room = generator._generate_empty_room(2, 5)
        
        assert isinstance(room, EmptyRoom)
        assert room.position == 2
        assert room.total_rooms == 5

    def test_select_room_type(self):
        """Тест выбора типа комнаты."""
        generator = RoomGenerator()
        room_type = generator._select_room_type(1, 5)
        
        # Должен быть один из допустимых типов (кроме BOSS)
        assert room_type in [RoomType.BATTLE, RoomType.TREASURE, RoomType.EMPTY]

    def test_generate_enemies(self):
        """Тест генерации врагов."""
        generator = RoomGenerator()
        enemies = generator._generate_enemies(3, 2, 1, 5)
        
        assert len(enemies) == 3
        for enemy in enemies:
            assert 'role' in enemy
            assert 'level' in enemy
            assert enemy['level'] >= 1


if __name__ == "__main__":
    pytest.main([__file__])