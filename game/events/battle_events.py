"""Модуль событий, связанных с боем."""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from unittest import result
from game.events.event import Event
from game.entities.character import Character


@dataclass
class BattleStartedEvent(Event):
    """Событие начала боя."""
    players: Optional[List[Character]] = None
    enemies: Optional[List[Character]] = None

@dataclass
class BattleEndedEvent(Event):
    """Событие окончания боя."""
    players: Optional[List[Character]] = None
    enemies: Optional[List[Character]] = None
    result: str = ""


@dataclass
class RoundStartedEvent(Event):
    """Событие начала раунда боя."""
    round_number: int = 0


@dataclass
class RoundEndedEvent(Event):
    """Событие окончания раунда боя."""
    round_number: int = 0


@dataclass
class TurnStartedEvent(Event):
    """Событие начала хода персонажа."""
    character: Optional[Character] = None
    source: Any = field(default=None)


@dataclass
class TurnEndedEvent(Event):
    """Событие окончания хода персонажа."""
    character: Optional[Character] = None
    source: Any = field(default=None)


@dataclass
class ActionExecutedEvent(Event):
    """Событие выполнения действия в бою."""
    character: Optional[Character] = None
    action: Any = field(default=None)
    target: Optional[Character] = None
    result: Any = field(default=None)
    source: Any = field(default=None)


@dataclass
class TurnSkippedEvent(Event):
    """Событие пропуска хода."""
    character: Optional[Character] = None
    source: Any = field(default=None)