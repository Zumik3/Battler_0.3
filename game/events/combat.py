# game/events/combat.py
"""События, связанные с боевой системой."""

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
from .event import Event

if TYPE_CHECKING:
    from game.entities.character import Character


@dataclass
class DamageEvent(Event):
    """Событие нанесения урона."""
    
    attacker: Optional['Character'] = None  # Кто наносит урон
    target: Optional['Character'] = None    # Кому наносится урон
    amount: int = 0                         # Количество урона
    damage_type: str = "physical"           # Тип урона (physical, fire, ice, etc.)
    is_critical: bool = False               # Критический ли удар
    can_be_blocked: bool = True             # Может ли быть заблокирован
    


@dataclass
class HealEvent(Event):
    """Событие лечения."""
    
    healer: Optional['Character'] = None
    target: Optional['Character'] = None
    amount: int = 0
    heal_type: str = "direct"


@dataclass
class DeathEvent(Event):
    """Событие смерти персонажа."""
    
    victim: Optional['Character'] = None
    killer: Optional['Character'] = None


@dataclass  
class CombatStartEvent(Event):
    """Событие начала боя."""
    participants: list['Character'] = []


@dataclass
class CombatEndEvent(Event):
    """Событие окончания боя."""
    winners: list['Character'] = []
    losers: list['Character'] = []