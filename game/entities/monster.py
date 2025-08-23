# game/entities/player.py
"""Класс монстра (персонажа, не управляемого игроком)."""

from typing import Optional, TYPE_CHECKING

from game.entities.character import Character
from game.factories.monster_property_factory import MonsterPropertyFactory

if TYPE_CHECKING:
    from game.entities.properties.experience import ExperienceProperty
    from game.factories.monster_factory import MonsterConfig
    from game.core.character_context import CharacterContext


class Monster(Character):
    """Класс для всех монстров (персонажей, не управляемых игроком)."""

    experience: Optional['ExperienceProperty']

    def __init__(self, context: 'CharacterContext', config: 'MonsterConfig') -> None:
        """
        Инициализирует монстра.

        Args:
            context: Контекст игры.
            config: Конфигурация игрока.
        """
        # 1. Инициализируем базовый класс Character
        super().__init__(context=context, config=config)

        # 2. Создаем и устанавливаем специфичные для игрока свойства
        #    с помощью фабрики
        _ = MonsterPropertyFactory(context=context, config=config, monster=self)
        #property_factory.create_advanced_properties(self)

        # 3. Дополнительная инициализация, специфичная для Monster, может быть здесь
        # ...