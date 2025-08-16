# game/ui/widgets/__init__.py
"""Переиспользуемые UI компоненты."""

from .labels import (
    TextLabel,
    CharacterNameLabel,
    CharacterClassLabel,
    CharacterLevelLabel
)

from .bars import (
    ProgressBar,
    HealthBar,
    EnergyBar
)

__all__ = [
    'TextLabel',
    'CharacterNameLabel',
    'CharacterClassLabel',
    'CharacterLevelLabel',
    'ProgressBar',
    'HealthBar',
    'EnergyBar',
]