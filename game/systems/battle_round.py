"""Модуль, содержащий класс для управления отдельным раундом боя."""

from __future__ import annotations
import time
from typing import List, Optional, TYPE_CHECKING

from game.actions.action import Action
from game.actions.basic_attack import BasicAttack
from game.events.battle_events import (
        RoundStartedEvent, RoundEndedEvent, TurnStartedEvent, TurnSkippedEvent
    )
from game.events.render_data import RenderData
from game.ui.rendering.color_manager import Color

if TYPE_CHECKING:
    from game.entities.character import Character
    from game.core.context import GameContext
    

class BattleRound:
    """Управляет одним раундом автоматического боя."""

    def __init__(self, context: GameContext, round_number: int, 
                 players: List[Character], enemies: List[Character]) -> None:
        """Инициализирует раунд боя.

        Args:
            context: Игровой контекст с доступом к системным сервисам.
            round_number: Номер текущего раунда.
            players: Список персонажей игроков.
            enemies: Список врагов для боя.
        """
        self.context = context
        self.round_number = round_number
        self.players = players
        self.enemies = enemies
        self.action_delay = 0.5  # Задержка между действиями в раунде

    def execute(self) -> None:
        """Выполняет все действия в рамках одного раунда."""
        # Публикуем событие начала раунда
        round_started_event = RoundStartedEvent(
            source=None,
            round_number=self.round_number,
            render_data=RenderData(template="--------------------(%1 раунд)--------------------",
                replacements={"1": (f"{self.round_number}", Color.GRAY, False, False)})
        )
        self.context.event_bus.publish(round_started_event)

        # Получаем порядок ходов
        turn_order = self._get_turn_order()

        for participant in turn_order:
            # Проверяем, не закончился ли бой досрочно
            if self._is_battle_over():
                break

            if not participant.is_alive():
                continue

            # Выполняем действие участника
            self._execute_participant_turn(participant)

            # Задержка между действиями для визуального эффекта
            if not self._is_battle_over():
                time.sleep(self.action_delay)

        # Публикуем событие конца раунда
        round_ended_event = RoundEndedEvent(
            round_number=self.round_number,
            source=self
        )
        self.context.event_bus.publish(round_ended_event)

    def _get_turn_order(self) -> List[Character]:
        """Определяет порядок ходов в раунде.

        Returns:
            Список персонажей в порядке их хода.
        """
        # TODO: Реализовать расчет на основе статов
        alive_participants = self._get_alive_participants()
        return alive_participants

    def _get_alive_participants(self) -> List[Character]:
        """Возвращает список всех живых участников боя.

        Returns:
            Список живых персонажей и врагов.
        """
        alive_players = [p for p in self.players if p.is_alive()]
        alive_enemies = [e for e in self.enemies if e.is_alive()]
        return alive_players + alive_enemies

    def _execute_participant_turn(self, character: Character) -> None:
        """Выполняет ход участника.

        Args:
            participant: Персонаж, выполняющий действие.
        """
        # Логика выбора действия
        action = self._choose_action(character)
        target = self._choose_target(character)

        if action and target:
            # Выполняем выбранное действие
            action.set_target(target)
            action.execute()
        else:
            # Публикуем событие пропуска хода
            turn_skipped_event = TurnSkippedEvent(
                character=character,
                source=self
            )
            self.context.event_bus.publish(turn_skipped_event)

    def _choose_action(self, character: Character) -> 'Action':
        """Выбирает действие для персонажа.

        Args:
            character: Персонаж, выбирающий действие.

        Returns:
            Выбранное действие или None.
        """
        # TODO: Реализовать логику выбора действия
        return BasicAttack(character)
        #return getattr(participant, 'get_basic_attack', lambda: None)()

    def _choose_target(self, attacker: Character) -> Optional[Character]:
        """Выбирает цель для атаки.

        Args:
            attacker: Атакующий персонаж.

        Returns:
            Цель для атаки или None.
        """
        if attacker in self.players:
            potential_targets = [e for e in self.enemies if e.is_alive()]
        else:
            potential_targets = [p for p in self.players if p.is_alive()]

        # return random.choice(potential_targets) if potential_targets else None
        return next((target for target in potential_targets), None)

    def _is_battle_over(self) -> bool:
        """Проверяет условия окончания боя.

        Returns:
            True, если бой завершен, иначе False.
        """
        all_players_dead = all(not player.is_alive() for player in self.players)
        all_enemies_dead = all(not enemy.is_alive() for enemy in self.enemies)
        return all_players_dead or all_enemies_dead