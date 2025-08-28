# game/systems/encounters/encounter_manager.py
"""Модуль, содержащий менеджер для управления походами (Encounter)."""

import random
from typing import List, TYPE_CHECKING

from game.systems.encounters.encounter import Encounter
from game.systems.encounters.events import BattleEncounterEvent
from game.events.battle_events import BattleEndedEvent
from game.systems.encounters.encounter_generator import EncounterGenerator
from game.systems.encounters.room_generator import RoomGenerator
from game.systems.encounters.room_sequence import RoomSequence
from game.events.encounter_events import RoomSequenceStartedEvent, RoomCompletedEvent, RoomSequenceCompletedEvent

if TYPE_CHECKING:
    from game.game_manager import GameManager
    from game.entities.player import Player
    from game.systems.encounters.room import Room
    from game.systems.encounters.room_sequence import RoomSequence

class EncounterManager:
    """
    Управляет созданиением, выполнением и состоянием походов.
    """

    def __init__(self, game_manager: 'GameManager'):
        """
        Инициализирует менеджер походов.

        Args:
            game_manager: Экземпляр GameManager для доступа к другим системам.
        """
        self.game_manager = game_manager
        self.current_encounter: 'Encounter' | None = None
        self.current_event_index: int = -1
        self.encounter_generator = EncounterGenerator()
        self.room_generator = RoomGenerator()
        self.current_room_sequence: RoomSequence | None = None
        self._setup_subscriptions()

    def _setup_subscriptions(self) -> None:
        """Подписывается на события, необходимые для управления походом."""
        self.game_manager.event_bus.subscribe(None, BattleEndedEvent, self._on_battle_ended)

    def generate_encounters(self, count: int = 3) -> List['Encounter']:
        """
        Генерирует список случайных походов на основе уровня группы игроков.
        
        Args:
            count: Количество походов для генерации.

        Returns:
            Список сгенерированных походов.
        """
        # Получаем группу игроков
        player_group = self.game_manager.get_player_group()
        
        # Если нет игроков, генерируем стандартные encounter'ы
        if not player_group:
            return self._generate_default_encounters(count)
            
        # Генерируем encounter'ы на основе уровня группы
        encounters = []
        for _ in range(count):
            # Для новых encounter'ев генерируем последовательности комнат
            encounter = self._generate_room_sequence_encounter(player_group)
            encounters.append(encounter)
            
        return encounters

    def _generate_room_sequence_encounter(self, player_group: List['Player']) -> 'Encounter':
        """
        Генерирует encounter с последовательностью комнат.
        
        Args:
            player_group: Группа игроков
            
        Returns:
            Encounter с последовательностью комнат
        """
        # Рассчитываем средний уровень группы
        levels = [player.level.level for player in player_group]
        avg_level = round(sum(levels) / len(levels)) if levels else 1
        
        # Определяем количество комнат в зависимости от уровня
        if avg_level <= 2:
            room_count = 2
        elif avg_level <= 5:
            room_count = random.randint(3, 4)
        else:
            room_count = random.randint(4, 6)
            
        # Генерируем комнаты
        rooms = []
        for i in range(room_count):
            room = self.room_generator.generate_room(i, room_count, avg_level)
            rooms.append(room)
            
        # Создаем последовательность комнат
        room_sequence = RoomSequence(rooms)
        room_sequence.set_name(f"Подземелье уровня {avg_level}")
        room_sequence.set_description(f"Последовательность из {room_count} комнат")
        
        # Сохраняем последовательность
        self.current_room_sequence = room_sequence
        
        # Создаем encounter с первой комнатой
        first_room = room_sequence.start()
        if first_room and hasattr(first_room, 'enemies'):
            # Для боевой комнаты создаем BattleEncounterEvent
            battle_event = BattleEncounterEvent(enemies=first_room.enemies)
            encounter = Encounter(
                name=room_sequence.name,
                description=room_sequence.description,
                difficulty=self._determine_difficulty(avg_level),
                events=[battle_event]
            )
        else:
            # Для других типов комнат создаем пустой encounter
            encounter = Encounter(
                name=room_sequence.name,
                description=room_sequence.description,
                difficulty=self._determine_difficulty(avg_level),
                events=[]
            )
            
        return encounter

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

    def _generate_default_encounters(self, count: int = 3) -> List['Encounter']:
        """
        Генерирует список стандартных походов (fallback, если нет игроков).
        
        Args:
            count: Количество походов для генерации.

        Returns:
            Список стандартных походов.
        """
        encounters = [
            Encounter(
                name="Легкая прогулка",
                description="Пара гоблинов преградила вам путь.",
                difficulty="Легко",
                events=[
                    BattleEncounterEvent(enemies=[
                        {'role': 'goblin', 'level': 1},
                        {'role': 'goblin', 'level': 1}
                    ])
                ]
            ),
            Encounter(
                name="Засада в лесу",
                description="Орк и два гоблина-приспешника.",
                difficulty="Средне",
                events=[
                    BattleEncounterEvent(enemies=[
                        {'role': 'goblin', 'level': 1},
                        {'role': 'orc', 'level': 2},
                        {'role': 'goblin', 'level': 1}
                    ])
                ]
            ),
            Encounter(
                name="Логово тролля",
                description="Вы нашли логово тролля. Он выглядит голодным.",
                difficulty="Сложно",
                events=[
                    BattleEncounterEvent(enemies=[
                        {'role': 'troll', 'level': 15}
                    ])
                ]
            )
        ]
        return encounters[:count]

    def init_encounter(self, encounter: 'Encounter') -> None:
        self.current_encounter = encounter
        self.current_event_index = 0

    def start_encounter(self, encounter: 'Encounter') -> None:
        """
        Начинает выбранный поход.

        Args:
            encounter: Экземпляр похода для запуска.
        """
        # Публикуем событие начала последовательности комнат, если есть
        if self.current_room_sequence:
            event_bus = self.game_manager.event_bus
            start_event = RoomSequenceStartedEvent(
                source=None,
                room_sequence=self.current_room_sequence,
                sequence_name=self.current_room_sequence.name
            )
            event_bus.publish(start_event)
            
        self._execute_current_event()

    def _execute_current_event(self) -> None:
        """Выполняет текущее событие в походе."""
        if self.current_encounter and 0 <= self.current_event_index < len(self.current_encounter.events):
            event = self.current_encounter.events[self.current_event_index]
            event.execute(self.game_manager)
        else:
            self._end_encounter()

    def get_current_event(self):
        """Возвращает текущее событие, если оно есть."""
        if self.current_encounter and 0 <= self.current_event_index < len(self.current_encounter.events):
            return self.current_encounter.events[self.current_event_index]
        return None

    def _on_battle_ended(self, event: BattleEndedEvent) -> None:
        """Обработчик события завершения боя."""
        if not self.current_encounter:
            return

        # Проверяем результат боя
        if event.result and event.result.alive_players:
            # Победа в бою
            self._on_battle_won()
        else:
            # Поражение в бою
            self._on_battle_lost()

    def _on_battle_won(self) -> None:
        """Обработчик победы в бою."""
        # Помечаем текущую комнату как пройденную
        if self.current_room_sequence:
            self.current_room_sequence.complete_current_room()

            # Публикуем событие завершения комнаты
            event_bus = self.game_manager.event_bus
            room_completed_event = RoomCompletedEvent(
                source=None,
                room=self.current_room_sequence.get_current_room(),
                room_position=self.current_room_sequence.progress.current_room_index,
                success=True
            )
            event_bus.publish(room_completed_event)

            # Проверяем, завершена ли вся последовательность
            if self.current_room_sequence.is_completed():
                self._on_sequence_completed(victory=True)
            # else:
            #     # Теперь переход к следующей комнате будет инициироваться UI
            #     # self._advance_to_next_room()
        else:
            # Если нет последовательности комнат, просто завершаем encounter
            self.current_event_index += 1
            if self.current_encounter and self.current_event_index >= len(self.current_encounter.events):
                self._end_encounter(is_victory=True)
            else:
                self._execute_current_event()

    def _on_battle_lost(self) -> None:
        """Обработчик поражения в бою."""
        # Помечаем текущую комнату как проваленную
        if self.current_room_sequence:
            current_room = self.current_room_sequence.get_current_room()
            if current_room:
                current_room.fail()
                
            # Публикуем событие провала комнаты
            event_bus = self.game_manager.event_bus
            room_completed_event = RoomCompletedEvent(
                source=None,
                room=current_room,
                room_position=self.current_room_sequence.progress.current_room_index,
                success=False
            )
            event_bus.publish(room_completed_event)
            
            # Завершаем encounter с поражением
            self._on_sequence_completed(victory=False)
        else:
            # Если нет последовательности комнат, завершаем как раньше
            self._end_encounter(is_victory=False)

    def advance_to_next_room(self) -> bool:
        """
        Переходит к следующей комнате в последовательности и подготавливает
        новое событие боя.
        Возвращает True, если есть следующая комната, иначе False.
        """
        if not self.current_room_sequence or self.current_room_sequence.is_completed():
            return False

        next_room = self.current_room_sequence.advance_to_next_room()
        if next_room and hasattr(next_room, 'enemies'):
            # Обновляем encounter с данными из новой комнаты
            if self.current_encounter:
                # Создаем новое событие боя для следующей комнаты
                battle_event = BattleEncounterEvent(enemies=next_room.enemies)
                self.current_encounter.events = [battle_event]
                self.current_event_index = 0
                # self._execute_current_event() # Выполнение будет инициировано UI
                return True

        return False

    def _on_sequence_completed(self, victory: bool = True) -> None:
        """Обработчик завершения всей последовательности комнат."""
        if not self.current_room_sequence:
            return
            
        # Публикуем событие завершения последовательности
        event_bus = self.game_manager.event_bus
        sequence_completed_event = RoomSequenceCompletedEvent(
            source=None,
            room_sequence=self.current_room_sequence,
            sequence_name=self.current_room_sequence.name,
            success=victory,
            total_rooms=self.current_room_sequence.get_total_rooms(),
            completed_rooms=self.current_room_sequence.get_completed_rooms_count()
        )
        event_bus.publish(sequence_completed_event)
        
        # Завершаем encounter
        self._end_encounter(is_victory=victory)

    def _end_encounter(self, is_victory: bool = True) -> None:
        """Завершает текущий поход."""
        # TODO: Показать экран с результатами (победа/поражение)
        # TODO: Выдать награды в случае победы
        
        print(f"Поход завершен. Результат: {'Победа' if is_victory else 'Поражение'}")

        self.current_encounter = None
        self.current_event_index = -1
        self.current_room_sequence = None
        
        # Возвращаем игрока на главный экран
        # self.game_manager.screen_manager.change_screen("main")