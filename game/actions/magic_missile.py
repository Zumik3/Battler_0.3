# game/actions/magic_missile.py
"""Модуль реализует действие магической ракеты."""
from typing import TYPE_CHECKING
from game.actions.action import Action
from game.events.combat import DamageEvent
from game.systems.combat.damage_type import DamageType # Импортируем Enum
from game.ui.rendering.color_manager import Color
from game.ui.rendering.render_data_builder import RenderDataBuilder

if TYPE_CHECKING:
    from game.entities.character import Character
    from game.events.render_data import RenderData

class MagicMissile(Action):
    """Действие магической ракеты.
    Наносит урон цели на основе интеллекта источника.
    Взаимодействие происходит через публикацию событий DamageEvent.
    """

    def __init__(self, source: 'Character') -> None:
        """Инициализирует действие магической ракеты.
        Args:
            source: Персонаж, выполняющий атаку.
        """
        # Приоритет ниже, чем у BasicAttack (10), например 8
        super().__init__(source, priority=8)
        self._energy_cost = 5  # Как у BasicAttack
        self._cooldown = 1     # Пример кулдауна, можно изменить

    @property
    def name(self) -> str:
        """Возвращает имя действия."""
        return "MagicMissile"

    def is_available(self) -> bool:
        """Проверяет, доступна ли магическая ракета.
        Returns:
            True если у источника достаточно энергии и есть цель, иначе False.
        """
        # Проверяем энергию
        has_energy = (
            self.source.energy is not None and
            self.source.energy.energy >= self.energy_cost
        )
        # Проверяем, есть ли цель (можно усложнить)
        has_target = bool(self.targets)

        return has_energy and has_target

    def _calculate_damage(self, target: 'Character') -> int:
        """Рассчитывает урон магической ракеты.
        Пример формулы: Базовый урон + (Интеллект источника * Модификатор)
        Args:
            target: Цель атаки.
        Returns:
            Рассчитанное значение урона.
        """
        base_damage = 10 # Базовый урон
        intelligence_bonus = 0
        if hasattr(self.source, 'stats') and self.source.stats:
            # Бонус от интеллекта, например 1 урона за 2 интеллекта
            intelligence_bonus = getattr(self.source.stats, 'intelligence', 0) // 2

        # Можно добавить зависимость от защиты цели, если нужно
        # defense_reduction = target.combat.defense if target.combat else 0
        # total_damage = max(1, base_damage + intelligence_bonus - defense_reduction // 2)

        total_damage = base_damage + intelligence_bonus
        return max(1, total_damage) # Урон не может быть меньше 1

    def _create_damage_render_data(self, attacker: 'Character', damage: int, target: 'Character') -> 'RenderData':
        """Создает данные для отображения урона.
        Args:
            attacker: Персонаж, наносящий урон.
            damage: Нанесенный урон.
            target: Цель урона.
        Returns:
            Объект RenderData.
        """
        return (RenderDataBuilder()
            .add_character_name(attacker)
            .add_text(" выпускает магическую ракету в ")
            .add_character_name(target)
            .add_text(" и наносит ")
            .add_damage_value(damage)
            .add_text(" урона")
            .build())

    def _execute(self) -> None:
        """Выполняет магическую ракету через публикацию событий.
        Создает и публикует DamageEvent для нанесения урона.
        """
        if not self.targets:
            # Лучше логировать ошибку или вызвать исключение
            # print("Нет цели для магической ракеты!")
            return

        self._spend_energy()
        target = self.targets[0] # Атакуем первую цель из списка

        # Рассчитываем урон
        damage = self._calculate_damage(target)

        # Создаем данные для отображения
        render_data = self._create_damage_render_data(
            attacker=self.source,
            damage=damage,
            target=target
        )

        # Создаем и публикуем событие нанесения урона
        damage_event = DamageEvent(
            source=None, # Источник события - сама система
            attacker=self.source,
            target=target,
            amount=damage,
            damage_type=DamageType.FIRE, # Предполагаем, что такой тип существует
            is_critical=False, # Можно добавить логику критов
            can_be_blocked=True, # Можно сделать блокируемым или нет
            render_data=render_data
        )
        self.source.context.event_bus.publish(damage_event)
