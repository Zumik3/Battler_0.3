"""
Модуль определяет абстрактный базовый класс для всех действий в бою.
Действия представляют собой способности, которые могут использовать персонажи.
"""
from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

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
        self.target: Optional['Character'] = None
        self._is_executed = False

    @property
    @abstractmethod
    def name(self) -> str:
        """Возвращает название действия."""
        pass

    @property
    @abstractmethod
    def energy_cost(self) -> int:
        """Возвращает стоимость энергии для выполнения действия."""
        pass

    def set_target(self, target: 'Character') -> None:
        """
        Устанавливает цель для действия.

        Args:
            target: Целевой персонаж.
        """
        self.target = target

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
        
        if not self.target:
            raise ValueError("Цель для действия не установлена.")
        
        if not self.is_available():
            raise RuntimeError("Попытка выполнить недоступное действие.")

        self._is_executed = True
        self._execute()