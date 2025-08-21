# game/events/combat.py
"""События, связанные с боевой системой."""

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING

from game.systems.damage.damage_type import PHYSICAL
from .event import Event

if TYPE_CHECKING:
    from game.entities.character import Character
    from game.systems.damage.damage_type import DamageType


@dataclass
class DamageEvent(Event):
    """Событие нанесения урона."""
    
    attacker: Optional['Character'] = None  # Кто наносит урон
    target: Optional['Character'] = None    # Кому наносится урон
    amount: int = 0                         # Количество урона
    damage_type: 'DamageType' = PHYSICAL           # Тип урона (physical, fire, ice, etc.)
    is_critical: bool = False               # Критический ли удар
    can_be_blocked: bool = True             # Может ли быть заблокирован

@dataclass
class EnergySpentEvent(Event):
    """Событие траты энергии персонажем."""
    
    character: Optional['Character'] = None  # Кто тратит энергию
    amount: int = 0                          # Количество потраченной энергии
    reason: str = ""                         # Причина траты (например, "basic_attack")


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
class LogUpdatedEvent(Event):
    """Событие обновления лога."""

    need_render: bool = True

