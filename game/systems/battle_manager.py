"""Менеджер боя для автоматического пошагового сражения."""

from __future__ import annotations
import time
from typing import List, TYPE_CHECKING
from game.events.battle_events import BattleStartedEvent, BattleEndedEvent


from game.ui.controllers.battle_log_controller import BattleLogController

if TYPE_CHECKING:
    from game.entities.character import Character
    from game.core.context import GameContext
    from game.systems.battle_round import BattleRound
    from game.ui.components.battle_components import BattleLog
    from game.systems.event_bus import EventBus
    


class BattleManager:
    """Управляет автоматическим боем с раундами и задержками между действиями."""
    
    def __init__(self, context: GameContext) -> None:
        """Инициализирует менеджер боя.
        
        Args:
            context: Игровой контекст с доступом к системным сервисам.
        """
        self.context = context
        self.is_battle_active = False
        self.current_round_number = 0
        self.players: List[Character] = []
        self.enemies: List[Character] = []
        self._battle_log_controller = None
        
        # Настройки задержек (в секундах)
        self.round_delay = 2.0  # Задержка между раундами

    def start_battle(self, players: List[Character], enemies: List[Character]) -> None:
        """Запускает автоматический бой.
        
        Args:
            players: Список персонажей игроков.
            enemies: Список врагов для боя.
        """
        self.players = players
        self.enemies = enemies
        self.is_battle_active = True
        self.current_round_number = 0

        # Активируем баттл лог
        self._battle_log_controller.activate()
        
        # Публикуем событие начала боя
        battle_started_event = BattleStartedEvent(
            players=self.players,
            enemies=self.enemies,
            source=self
        )
        self.context.event_bus.publish(battle_started_event)
        
        # Основной цикл боя
        self._run_battle_loop()

        # Публикуем событие окончания боя
        battle_result = self.get_battle_result()
        battle_ended_event = BattleEndedEvent(
            result=battle_result,
            players=self.players,
            enemies=self.enemies,
            source=self
        )
        self.context.event_bus.publish(battle_ended_event)

        # Бой закончен
        self._battle_log_controller.deactivate()
    
    def _run_battle_loop(self) -> None:
        """Основной цикл управления боем."""
        while self.is_battle_active and not self._is_battle_over():
            self.current_round_number += 1
            
            # Создаем и выполняем раунд
            round_manager = self._create_round(self.current_round_number)
            round_manager.execute()
            
            # Задержка между раундами
            if self.is_battle_active and not self._is_battle_over():
                time.sleep(self.round_delay)
    
    def _create_round(self, round_number: int) -> BattleRound:
        """Фабричный метод для создания объекта раунда.
        
        Args:
            round_number: Номер создаваемого раунда.
            
        Returns:
            Экземпляр BattleRound для управления раундом.
        """
        from game.systems.battle_round import BattleRound
        return BattleRound(
            context=self.context,
            round_number=round_number,
            players=self.players,
            enemies=self.enemies
        )
    
    def _is_battle_over(self) -> bool:
        """Проверяет условия окончания боя.
        
        Returns:
            True, если бой завершен, иначе False.
        """
        all_players_dead = all(not player.is_alive() for player in self.players)
        all_enemies_dead = all(not enemy.is_alive() for enemy in self.enemies)
        return all_players_dead or all_enemies_dead
    
    def get_battle_result(self) -> str:
        """Возвращает результат боя.
        
        Returns:
            Строка с результатом: 'victory', 'defeat' или 'ongoing'.
        """
        if not self._is_battle_over():
            return "ongoing"
        
        all_players_dead = all(not player.is_alive() for player in self.players)
        all_enemies_dead = all(not enemy.is_alive() for enemy in self.enemies)
        
        if all_enemies_dead:
            return "victory"
        elif all_players_dead:
            return "defeat"
        else:
            return "ongoing"

    def setup_battle_log_controller(self, event_bus: 'EventBus', battle_log: 'BattleLog') -> None:
        self._battle_log_controller = BattleLogController(
            event_bus=event_bus, 
            battle_log=battle_log
        )