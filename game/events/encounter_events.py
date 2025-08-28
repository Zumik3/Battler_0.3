# game/events/encounter_events.py
"""События, связанные с комнатами и последовательностями encounter'ей."""

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from game.events.event import Event

if TYPE_CHECKING:
    from game.systems.encounters.room import Room
    from game.systems.encounters.room_sequence import RoomSequence


@dataclass
class RoomSequenceStartedEvent(Event):
    """Событие начала последовательности комнат."""
    room_sequence: Optional['RoomSequence'] = None
    sequence_name: str = ""


@dataclass
class RoomCompletedEvent(Event):
    """Событие завершения комнаты."""
    room: Optional['Room'] = None
    room_position: int = 0
    success: bool = True  # True для победы, False для поражения


@dataclass
class RoomTransitionEvent(Event):
    """Событие перехода между комнатами."""
    from_room: Optional['Room'] = None
    to_room: Optional['Room'] = None
    from_position: int = 0
    to_position: int = 0


@dataclass
class RoomSequenceCompletedEvent(Event):
    """Событие завершения всей последовательности комнат."""
    room_sequence: Optional['RoomSequence'] = None
    sequence_name: str = ""
    success: bool = True  # True для победы, False для поражения
    total_rooms: int = 0
    completed_rooms: int = 0