# game/systems/encounters/encounter.py
"""Модуль, определяющий структуру похода (Encounter)."""

from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from game.systems.encounters.events import EncounterEvent

@dataclass
class Encounter:
    """
    Датакласс, представляющий один поход (энкаунтер).

    Атрибуты:
        name (str): Название похода.
        description (str): Краткое описание.
        difficulty (str): Сложность (например, "Легко", "Средне", "Сложно").
        events (List[EncounterEvent]): Список событий, составляющих поход.
    """
    name: str
    description: str
    difficulty: str
    events: List['EncounterEvent'] = field(default_factory=list)