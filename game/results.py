# game/results.py
"""Типизированные классы для результатов действий."""

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ActionResult:
    """Базовый класс для результатов игровых действий."""
    type: str
    message: Optional[str] = None

@dataclass
class ExperienceGainedResult(ActionResult):
    """Результат получения опыта."""
    type: str = field(default="exp_gained")
    exp_amount: int = 0
    total_exp: int = 0

@dataclass
class LevelUpResult(ActionResult):
    """Результат повышения уровня."""
    type: str = field(default="level_up")
    character: str = ""
    new_level: int = 0

@dataclass
class LevelUpHealResult(ActionResult):
    """Результат исцеления при повышении уровня."""
    type: str = field(default="level_up_heal")
    character: str = ""
    hp_restored: int = 0
    energy_restored: int = 0

@dataclass
class DamageTakenResult(ActionResult):
    """Результат получения урона."""
    type: str = field(default="damage_taken")
    target: str = ""
    damage: int = 0
    hp_left: int = 0

@dataclass
class HealedResult(ActionResult):
    """Результат исцеления."""
    type: str = field(default="healed")
    target: str = ""
    heal_amount: int = 0
    hp_now: int = 0