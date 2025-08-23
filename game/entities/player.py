# game/entities/player.py
"""Класс игрока (персонажа, управляемого игроком)."""

from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING


from game.entities.character import Character
from game.factories.player_property_factory import PlayerPropertyFactory

if TYPE_CHECKING:
    from game.entities.properties.experience import ExperienceProperty
    from game.factories.player_factory import PlayerConfig
    from game.core.character_context import CharacterContext
    from game.core.game_context import GameContext


class Player(Character):
    """Класс для всех игроков (персонажей, управляемых игроком)."""

    experience: Optional['ExperienceProperty']

    def __init__(self, context: 'CharacterContext', game_context: 'GameContext', config: 'PlayerConfig') -> None:
        """
        Инициализирует игрока.

        Args:
            context: Контекст игры.
            config: Конфигурация игрока.
        """
        # 1. Инициализируем базовый класс Character
        super().__init__(context=context, config=config)

        # 2. Создаем и устанавливаем специфичные для игрока свойства
        #    с помощью фабрики
        _ = PlayerPropertyFactory(context=context, game_context=game_context, config=config, player=self)
        #property_factory.create_advanced_properties(self)

        # 3. Дополнительная инициализация, специфичная для Player, может быть здесь
        # ...