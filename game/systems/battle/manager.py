# game/systems/battle_manager.py
"""Менеджер боя для автоматического пошагового сражения."""

from __future__ import annotations
import time
from typing import List, TYPE_CHECKING
from game.events.battle_events import BattleStartedEvent, BattleEndedEvent

# Добавляем импорт BattleResult
from game.systems.battle.result import BattleResult

from game.events.render_data import RenderData
from game.ui.controllers.battle_log_controller import BattleLogController
from game.ui.rendering.color_manager import Color

if TYPE_CHECKING:
    from game.entities.character import Character
    from game.core.context import GameContext
    from game.systems.battle.round import BattleRound
    from game.ui.components.battle_components import BattleLog
    from game.systems.events.bus import EventBus
    


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
            source=None,
            render_data=RenderData(template="%1 начинается...",
                replacements={"1": ("Бой", Color.RED, True, False)})
            )  # Вынести в отдельный файл - именно формирование сообщения
        
        self.context.event_bus.publish(battle_started_event)
        
        # Основной цикл боя
        self._run_battle_loop()

        # --- ИЗМЕНЕНИЯ НАЧАЛО ---
        # Создаем BattleResult *после* окончания боя
        battle_result_obj = BattleResult(
            players=self.players,
            enemies=self.enemies,
            alive_players=[p for p in self.players if p.is_alive()],
            dead_enemies=[e for e in self.enemies if not e.is_alive()],
            # battle_log=None, # Пока не заполняем
            # battle_id=None, # Пока не заполняем
        )

        # Публикуем событие окончания боя с BattleResult
        battle_ended_event = BattleEndedEvent(
            # Передаем объект BattleResult, а не строку
            result=battle_result_obj,
            source=None,
            render_data=RenderData(template="%1 завершен...",
                replacements={"1": ("Бой", Color.RED, True, False)})
            )
        # --- ИЗМЕНЕНИЯ КОНЕЦ ---

        self.context.event_bus.publish(battle_ended_event)

        # Бой закончен
        self._battle_log_controller.deactivate()
    
    def _run_battle_loop(self) -> None:
        """Основной цикл управления боем."""
        while self.is_battle_active and not self._is_battle_over():
            self.current_round_number += 1
            
            # Создаем и выполняем раунд
            battle_round = self._create_round(self.current_round_number)
            battle_round.execute()
            
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
        from game.systems.battle.round import BattleRound
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
