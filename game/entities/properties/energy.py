# game/entities/components/energy.py
"""Свойство энергии персонажа."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from game.protocols import EnergyPropertyProtocol, StatsProtocol
from game.entities.properties.property import DependentProperty 
from game.events.character import StatsChangedEvent
from game.events.combat import EnergySpentEvent

@dataclass
class EnergyProperty(DependentProperty, EnergyPropertyProtocol):
    """Свойство для управления энергией персонажа.
    
    Атрибуты:
        max_energy: Максимальный запас энергии.
        energy: Текущий запас энергии.
        stats: Ссылка на объект статов, от которых зависит свойство.
               (добавлено, так как DependentProperty его не предоставляет)
        # Атрибуты context, _is_subscribed наследуются от DependentProperty.
    """
    
    # Именованные константы для расчета энергии
    BASE_ENERGY: int = field(default=100, init=False, repr=False)
    ENERGY_PER_INTELLIGENCE: int = field(default=10, init=False, repr=False)
    
    max_energy: int = field(default=0)
    energy: int = field(default=0)
    stats: Optional[StatsProtocol] = field(default=None)
    
    def __post_init__(self) -> None:
        """Инициализация свойства энергии."""
        super().__post_init__()
        if self.stats:
            self._recalculate()
            if self.energy == 0:
                self.energy = self.max_energy
    
    def _setup_subscriptions(self) -> None:
        """Подписывается на изменения статов."""
        # Проверяем, не подписаны ли мы уже и существуют ли необходимые зависимости
        if not self._is_subscribed and self.stats and self.context:
            self._subscribe_to(self.stats, StatsChangedEvent, self._on_stats_event)
            self._subscribe_to(None, EnergySpentEvent, self._on_energy_spent)
            self._is_subscribed = True

    def _on_stats_event(self, event: StatsChangedEvent) -> None:
        """Вызывается при получении события изменения статов."""
        self._recalculate_from_stats(event.source)

    def _on_energy_spent(self, event: EnergySpentEvent) -> None:
        """Вызывается при получении события траты энергии."""
        if self.context.character is event.character:
            self.spend_energy(event.amount)
        
    def _recalculate_from_stats(self, stats: StatsProtocol) -> None:
        """Пересчитывает свойство на основе статов."""
        self._recalculate()

    def _recalculate(self) -> None:
        """Пересчитывает максимальную энергию на основе intelligence.
        
        Использует формулу: 
        max_energy = BASE_ENERGY + (intelligence * ENERGY_PER_INTELLIGENCE)
        """
        if not self.stats:
            self.max_energy = self.BASE_ENERGY
            if self.energy > self.max_energy or self.energy == 0:
                self.energy = self.max_energy
            return
            
        new_max_energy = self.BASE_ENERGY + (
            getattr(self.stats, 'intelligence', 0) * self.ENERGY_PER_INTELLIGENCE
        )
        self.max_energy = new_max_energy
        
        self.restore_full_energy()

    def get(self):
        return self.energy

    def restore_energy(
        self, 
        amount: Optional[int] = None, 
        percentage: Optional[float] = None
        ) -> None:
        """Восстанавливает энергию персонажа.
        
        Восстановление происходит по одному из трех сценариев:
        1. Если указан `percentage`, восстанавливается процент от максимальной энергии.
        2. Если указан `amount`, восстанавливается конкретное количество энергии.
        3. Если ничего не указано, энергия восстанавливается полностью.
        
        Args:
            amount: Конкретное количество энергии для восстановления.
                    Используется, если `percentage` не указан.
            percentage: Процент максимальной энергии для восстановления.
                        Должен быть в диапазоне 0.0 - 100.0.
                        
        """
        old_energy = self.energy

        if percentage is not None:
            restore_amount = int(self.max_energy * (percentage / 100.0))
            self.energy = min(self.max_energy, self.energy + restore_amount)
        elif amount is not None:
            self.energy = min(self.max_energy, self.energy + amount)
        else:
            self.energy = self.max_energy
    
    def spend_energy(self, amount: int) -> bool:
        """Тратит энергию персонажа.
        
        Args:
            amount: Количество энергии, которое нужно потратить.
            
        Returns:
            True, если энергия была успешно потрачена (хватило энергии).
            False, если энергии недостаточно.
        """
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False
    
    def restore_full_energy(self) -> None:
        """Полностью восстанавливает энергию.
        
        Устанавливает текущую энергию равной максимальной.
        """
        self.energy = self.max_energy
