# game/systems/encounters/manager.py
"""Модуль, содержащий менеджер для управления походами (Encounter)."""

from typing import List, TYPE_CHECKING

from game.systems.encounters.encounter import Encounter
from game.systems.encounters.events import BattleEncounterEvent
from game.events.battle_events import BattleEndedEvent

if TYPE_CHECKING:
    from game.game_manager import GameManager

class EncounterManager:
    """
    Управляет созданием, выполнением и состоянием походов.
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
        self._setup_subscriptions()

    def _setup_subscriptions(self) -> None:
        """Подписывается на события, необходимые для управления походом."""
        self.game_manager.event_bus.subscribe(None, BattleEndedEvent, self._on_battle_ended)

    def generate_encounters(self, count: int = 3) -> List['Encounter']:
        """
        Генерирует список случайных походов.
        
        Args:
            count: Количество походов для генерации.

        Returns:
            Список сгенерированных походов.
        """
        # TODO: Заменить на более сложную генерацию
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
                        {'role': 'troll', 'level': 5}
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
        self._execute_current_event()

    def _execute_current_event(self) -> None:
        """Выполняет текущее событие в походе."""
        if self.current_encounter and 0 <= self.current_event_index < len(self.current_encounter.events):
            event = self.current_encounter.events[self.current_event_index]
            event.execute(self.game_manager)
        else:
            self._end_encounter()

    def _on_battle_ended(self, event: BattleEndedEvent) -> None:
        """Обработчик события завершения боя."""
        if not self.current_encounter:
            return

        # Проверяем результат боя
        if event.result and event.result.alive_players:
            # Победа, продолжаем поход
            self.current_event_index += 1
            self._execute_current_event()
        else:
            # Поражение, завершаем поход
            self._end_encounter(is_victory=False)

    def _end_encounter(self, is_victory: bool = True) -> None:
        """Завершает текущий поход."""
        # TODO: Показать экран с результатами (победа/поражение)
        # TODO: Выдать награды в случае победы
        
        print(f"Поход завершен. Результат: {'Победа' if is_victory else 'Поражение'}")

        self.current_encounter = None
        self.current_event_index = -1
        
        # Возвращаем игрока на главный экран
        # self.game_manager.screen_manager.change_screen("main")