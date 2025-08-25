# game/entities/character.py
"""Базовый класс персонажа в игре."""

from abc import ABC
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, TYPE_CHECKING


from game.ai.decision_makers.basic_enemy_ai import BasicEnemyAI
from game.events.combat import DeathEvent
from game.events.render_data import RenderData

from game.ui.rendering.color_manager import Color

if TYPE_CHECKING:
    from game.entities.properties.combat import CombatProperty
    from game.entities.properties.health import HealthProperty
    from game.entities.properties.energy import EnergyProperty
    from game.entities.properties.level import LevelProperty
    from game.entities.properties.stats import StatsProperty
    from game.events.character import HealthChangedEvent
    from game.core.character_context import CharacterContext
    from game.protocols import AbilityManagerProtocol
    from game.ai.ai_decision_maker import AIDecisionMaker


# ==================== Вспомогательные классы ====================

@dataclass
class CharacterConfig:
    """Конфигурация для создания персонажа."""
    
    # Базовые параметры
    name: str
    role: str
   
    # Параметры для системы уровней/характеристик
    base_stats: Dict[str, int]
    growth_rates: Dict[str, float]
    level: int = 1
    is_player: bool = field(default=False)

    class_icon: str = "?"
    class_icon_color: str = ""
    description: str = ""
    starting_abilities: List[str] = field(default_factory=list)
    ai_config: Optional[Dict[str, Any]] = None


class Character(ABC):
    """Абстрактный базовый класс, представляющий персонажа в игре."""

    # Объявляем атрибуты на уровне класса для mypy
    context: 'CharacterContext'
    name: str
    role: str
    alive: bool
    is_player: bool
    class_icon: str
    class_icon_color: str
    
    
    # Атрибуты, которые будут заполнены фабрикой свойств
    stats: Optional['StatsProperty']
    level: Optional['LevelProperty']
    health: Optional['HealthProperty']
    energy: Optional['EnergyProperty']
    combat: Optional['CombatProperty']

    abilities: Optional['AbilityManagerProtocol'] = None
    ai: Optional['AIDecisionMaker'] = None

    def __init__(self, context: 'CharacterContext', config: 'CharacterConfig'):

        self.context = context
        self.context.set_base_characteristics(config.base_stats, config.growth_rates)

        self.alive = True
        self.name = config.name
        self.role = config.role
        self.is_player = config.is_player

        self.class_icon = config.class_icon
        self.class_icon_color = config.class_icon_color

    # ==================== Основные методы персонажа ====================
    def is_alive(self) -> bool:
        """Проверяет, жив ли персонаж."""
        return self.alive

    def _on_health_changed(self, event: 'HealthChangedEvent') -> None:
        if self.is_alive() and event.new_health <= 0:
            self._died()

    def _died(self) -> None:  # Будет привантым - никто не должен вызывать из вне - только через событие _on_health_changed
        """Убивает персонажа."""
        if self.is_alive():
            self.alive = False
            self.context.event_bus.publish(
                DeathEvent(
                    source=None,
                    victim=self,
                    render_data=RenderData(template="%1 умирает...",
                        replacements={"1": (f"{self.name}", Color.RED, True, False)})
                )
            )
