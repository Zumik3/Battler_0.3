"""
Модуль определяет абстрактный базовый класс для всех действий в бою.
Действия представляют собой способности, которые могут использовать персонажи.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Sequence

from game.events.combat import EnergySpentEvent

if TYPE_CHECKING:
    from game.entities.character import Character


class Action(ABC):
    """
    Абстрактный базовый класс для всех действий в бою.

    Атрибуты:
        source: Персонаж, который выполняет действие.
        target: Цель действия. Может быть None для действий без конкретной цели.
        priority: Приоритет действия для определения порядка в очереди ходов.
    """

    def __init__(self, source: 'Character', priority: int = 0) -> None:
        """
        Инициализирует действие.

        Args:
            source: Персонаж, источник действия.
            priority: Приоритет действия. По умолчанию 0.
        """
        self.source = source
        self.priority = priority
        self.targets: Sequence['Character'] = []
        self._is_executed = False
        self._energy_cost = 0
        self._cooldown = 0

    @property
    def name(self) -> str:
        """Возвращает название действия."""
        return type(self).__name__

    @property
    def energy_cost(self) -> int:
        """Возвращает стоимость энергии для выполнения действия."""
        return self._energy_cost

    @property
    def cooldown(self) -> int:
        """Возвращает кулдаун способности."""
        return self._cooldown

    def set_target(self, targets: Sequence['Character']) -> None:
        """
        Устанавливает цель для действия.

        Args:
            target: Целевой персонаж.
        """
        self.targets = targets

    @abstractmethod
    def is_available(self) -> bool:
        """
        Проверяет, доступно ли действие для выполнения.

        Returns:
            True если действие доступно, иначе False.
        """
        pass

    @abstractmethod
    def _execute(self) -> None:
        """
        Основная логика выполнения действия.
        Реализует побочные эффекты действия (нанесение урона, применение эффектов и т.д.).
        """
        pass

    def execute(self) -> None:
        """
        Выполняет действие.
        Побочные эффекты выполнения реализуются в методе _execute().

        Raises:
            ValueError: Если действие уже было выполнено или цель не установлена.
            RuntimeError: Если действие недоступно для выполнения.
        """
        if self._is_executed:
            raise ValueError("Действие уже было выполнено.")
        
        if not self.targets:
            raise ValueError("Цель для действия не установлена.")
        
        if not self.is_available():
            raise RuntimeError("Попытка выполнить недоступное действие.")

        self._is_executed = True
        self._execute()

    def _spend_energy(self) -> None:
        """
        Публикует событие траты энергии для источника действия.
        Использует self.source, self.energy_cost и self.name.
        """
        if self.source.context and self.source.context.event_bus:
            energy_event = EnergySpentEvent(
                source=None,
                character=self.source,
                amount=self.energy_cost,
                reason=f"action_{self.name}"
            )
            self.source.context.event_bus.publish(energy_event)
        # TODO: Возможно, обработать случай, если context или event_bus отсутствуют?
        # Например, логирование предупреждения или вызов исключения.
