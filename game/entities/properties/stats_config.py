"""Модуль свойства конфигурации характеристик персонажа."""

from dataclasses import dataclass, field
from typing import Dict, TypedDict

from game.protocols import StatsProtocol

# Типизированный словарь для всех характеристик
class AllStats(TypedDict):
    strength: int
    agility: int
    intelligence: int
    vitality: int

@dataclass
class BaseStats:
    """Датакласс базовых характеристик на 1 уровне."""
    strength: int = 10
    agility: int = 10
    intelligence: int = 10
    vitality: int = 10

@dataclass
class GrowthRates:
    """Датакласс коэффициентов роста характеристик."""
    strength: float = 0.1
    agility: float = 0.08
    intelligence: float = 0.12
    vitality: float = 0.15

@dataclass
class StatsConfigProperty:
    """Свойство для хранения базовых параметров характеристик.
    
    Attributes:
        base_stats: Базовые значения характеристик на 1 уровне.
        growth_rates: Коэффициенты роста характеристик.
    """
    
    base_stats: BaseStats = field(default_factory=BaseStats)
    growth_rates: GrowthRates = field(default_factory=GrowthRates)

    def get_base_stat(self, stat_name: str) -> int:
        """Возвращает базовое значение характеристики."""
        return getattr(self.base_stats, stat_name)

    def get_growth_rate(self, stat_name: str) -> float:
        """Возвращает коэффициент роста характеристики."""
        return getattr(self.growth_rates, stat_name)

    def _calculate_stat_at_level(self, stat_name: str, level: int) -> int:
        """Вычисляет значение характеристики на указанном уровне.
        
        Args:
            stat_name: Название характеристики.
            level: Уровень для расчета.
            
        Returns:
            Рассчитанное значение характеристики.
            
        Raises:
            AttributeError: Если характеристика не существует.
        """
        try:
            base_value = self.get_base_stat(stat_name)
            growth_rate = self.get_growth_rate(stat_name)
            return round(base_value + (base_value * growth_rate * (level - 1)))
        except AttributeError:
            raise AttributeError(f"Характеристика '{stat_name}' не существует")

    def calculate_all_stats_at_level(self, level: int) -> Dict[str, int]:
        """Вычисляет все характеристики на указанном уровне."""
        return {
            'strength': self._calculate_stat_at_level('strength', level),
            'agility': self._calculate_stat_at_level('agility', level),
            'intelligence': self._calculate_stat_at_level('intelligence', level),
            'vitality': self._calculate_stat_at_level('vitality', level)
        }

    def __str__(self) -> str:
        """Строковое представление конфигурации."""
        return f"StatsConfig(base={self.base_stats}, growth={self.growth_rates})"