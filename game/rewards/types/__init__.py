# game/rewards/types/__init__.py
"""Пакет конкретных типов наград."""

from .experience import ExperienceReward

# При добавлении новых типов наград, импортируйте их здесь также
# from .items import ItemReward
# ...

__all__ = [
    'ExperienceReward',
    # 'ItemReward',
    # ...
]
