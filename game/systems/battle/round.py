"""Модуль, содержащий класс для управления отдельным раундом боя."""

from __future__ import annotations
import time
from typing import List, Optional, TYPE_CHECKING, cast

from game.actions.action import Action
from game.actions.basic_attack import BasicAttack

from game.actions.basic_heal import BasicHeal
from game.events.battle_events import (
        RoundStartedEvent, RoundEndedEvent, TurnSkippedEvent
    )
from game.events.combat import LogUpdatedEvent
from game.events.render_data import RenderData
from game.ui.rendering.color_manager import Color
from game.ui.rendering.render_data_builder import RenderDataBuilder

if TYPE_CHECKING:
    from game.entities.character import Character
    from game.core.game_context import GameContext
    from game.entities.monster import Monster
    from game.entities.player import Player
    

class BattleRound:
    """Управляет одним раундом автоматического боя."""

    def __init__(self, context: 'GameContext', round_number: int, 
                 players: List['Player'], enemies: List['Monster']) -> None:
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
        self._event_bus = context.event_bus

    def execute(self) -> None:
        """Выполняет все действия в рамках одного раунда."""
        # Публикуем событие начала раунда
        # Используем RenderDataBuilder аналогично BasicAttack
        render_data = (RenderDataBuilder()
            .add_styled_text("･･････････････････ [ ", Color.GRAY, False, False)
            .add_styled_text("Раунд ", Color.CYAN, True, False)
            .add_styled_text(f"{self.round_number}", Color.YELLOW, True, False)
            .add_styled_text(" ] ･･････････････････", Color.GRAY, False, False)
            .build())
        
        round_started_event = RoundStartedEvent(
            source=None,
            round_number=self.round_number,
            render_data=render_data
        )
        self.context.event_bus.publish(round_started_event)
        time.sleep(self.action_delay)

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

            self._event_bus.publish(LogUpdatedEvent(source=None, need_render=True))

            # Задержка между действиями для визуального эффекта
            if not self._is_battle_over():
                time.sleep(self.action_delay)

        # Публикуем событие конца раунда
        round_ended_event = RoundEndedEvent(
            round_number=self.round_number,
            source=None
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
        return cast(List['Character'], alive_players + alive_enemies)

    def _execute_participant_turn(self, character: Character) -> None:
        """Выполняет ход участника.

        Args:
            character: Персонаж, выполняющий действие.
        """
        if character.ai:
            # Определяем союзников и врагов
            allies = self.players if character in self.players else self.enemies
            enemies = self.enemies if character in self.players else self.players

            alive_allies = [a for a in allies if a.is_alive()]
            alive_enemies = [e for e in enemies if e.is_alive()]
            
            # Вызываем ИИ для выбора действия
            ability_name, targets = character.ai.choose_action(character, alive_allies, alive_enemies)
            
            # Используем выбранную способность
            if ability_name and targets is not None:
                if character.abilities:
                    character.abilities.use_ability(ability_name, targets=targets)

    def _is_battle_over(self) -> bool:
        """Проверяет условия окончания боя.

        Returns:
            True, если бой завершен, иначе False.
        """
        all_players_dead = all(not player.is_alive() for player in self.players)
        all_enemies_dead = all(not enemy.is_alive() for enemy in self.enemies)
        return all_players_dead or all_enemies_dead