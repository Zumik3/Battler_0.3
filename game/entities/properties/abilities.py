# game/entities/properties/abilities.py
"""
Свойство способностей персонажа.
Управляет списком доступных способностей персонажа и логикой их использования.
"""

from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING, Optional

from game.entities.properties.property import DependentProperty
from game.events.combat import AbilityUsedEvent
from game.protocols import AbilityManagerProtocol

if TYPE_CHECKING:
    from game.entities.character import Character
    from game.protocols import AbilityRegistryProtocol 
    from game.systems.combat.cooldown_manager import CooldownManager


@dataclass
class Abilities(DependentProperty, AbilityManagerProtocol):
    """
    Свойство для управления способностями персонажа.
    
    Атрибуты:
        abilities: Список имен доступных способностей.
        context: Контекст свойства, предоставляющий доступ к event_bus и character.
                 Также будет предоставлять доступ к ability_registry.
    """
    abilities: List[str] = field(default_factory=list)
    ability_registry: Optional['AbilityRegistryProtocol'] = None
    cooldown_manager: Optional['CooldownManager'] = None

    # Контекст уже есть в DependentProperty как self.context: 'PropertyContext'
    # Если нужно напрямую работать с GameContext или CharacterContext, можно добавить:
    # character_context: Optional['CharacterContext'] = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Инициализация свойства способностей."""
        super().__post_init__()
        
        self._setup_subscriptions()

    def _setup_subscriptions(self) -> None:
        """Настраивает подписки на события, если необходимо."""
        pass

    # def _on_level_up(self, event: 'LevelUpEvent') -> None:
    #     """Обработчик события повышения уровня."""
    #     # Логика добавления новых способностей при повышении уровня
    #     pass

    # --- Методы из AbilityManagerProtocol ---

    def add_ability(self, ability_name: str) -> None:
        """
        Добавляет способность персонажу по имени.

        Args:
            ability_name: Имя способности для добавления.

        Returns:
            Список результатов действия (ActionResult).
        """
        # TODO: Проверка на дубликаты? Ограничения?
        if ability_name not in self.abilities:
            self.abilities.append(ability_name)
            # Можно опубликовать событие, например, AbilityLearnedEvent
            # self._publish_ability_learned(ability_name)

    def use_ability(self, ability_name: str, targets: List['Character'], **kwargs) -> None:
        """Использует способность по имени.

        Args:
            ability_name: Название способности для использования.
            target: Список целей.
            **kwargs: Дополнительные аргументы.
        """
        # 1. Проверить, есть ли способность в списке доступных
        if ability_name not in self.abilities:
            print(f"Способность '{ability_name}' недоступна для персонажа.")
            return

        # 2. Получить фабрику из реестра (через context)
        if not self.ability_registry or not self.ability_registry.is_registered(ability_name):
            print(f"Способность '{ability_name}' не найдена в реестре.")
            return

        try:
            factory = self.ability_registry.get_factory(ability_name)
            source_character = self.context.character
            action = factory(source_character)
            
            # 4. Настроить Action (цель, параметры)
            if targets:
                action.set_target(targets)
                
            # Добавляем другие параметры из kwargs если нужно
            for key, value in kwargs.items():
                if hasattr(action, key):
                    setattr(action, key, value)

            # 5. Выполнить Action (_execute или execute)
            # Используем публичный метод execute, который внутри вызывает _execute
            action.execute()

            # 6. Запустить кулдаун способности
            ability_event = AbilityUsedEvent(
                source=None,
                character=source_character,
                ability_name=action.name,
                cooldown=action.cooldown
            )
            self.context.event_bus.publish(ability_event)
            
        except Exception as e:
            pass

    def get_available_abilities(self) -> List[str]:
        """
        Получить список имен доступных способностей.

        Returns:
            Список имен способностей.
        """
        all_abilities = self.abilities.copy() # Возвращаем копию, чтобы не сломать внутренний список
        
        if self.cooldown_manager:
            return self.cooldown_manager.get_ready_abilities(self.context.character, all_abilities)
        else:
            return all_abilities

# Дополнительные классы, если нужно

# class Ability:
#     """Представление способности (шаблон/описание)."""
#     # Это может быть полезно, если мы хотим хранить больше информации,
#     # чем просто имя. Пока можно обойтись списком имен str.
#     def __init__(self, name: str, description: str = ""):
#         self.name = name
#     #     self.description = description




#  НЕ ТРОГАТЬ - это на будущее
# LevelUpEvent: Когда персонаж повышает уровень, он может получать новые способности или улучшать существующие. Abilities может подписаться на это событие, чтобы проверить, положено ли персонажу что-то новое, и добавить соответствующую способность из конфигурации класса.
# EquipItemEvent / UnequipItemEvent: Надетая экипировка может давать или убирать временный доступ к определенным способностям. Abilities может подписаться на эти события, чтобы динамически добавлять или убирать способности из своего списка abilities.
# LearnAbilityEvent: Специальное событие, публикуемое, например, при использовании свитка обучения или по завершении квеста. Abilities может подписаться на него, чтобы добавить новую способность.
# AbilityUsedEvent: Подписка на собственные же события использования способностей может понадобиться для отслеживания кулдаунов (если они будут реализованы на уровне свойства).
# EnterCombatEvent / ExitCombatEvent: Некоторые способности могут быть доступны только вне боя или наоборот. Свойство может подписаться на эти события, чтобы временно модифицировать список доступных способностей или блокировать их использование.
# StatusEffectAppliedEvent / StatusEffectRemovedEvent: Некоторые эффекты (например, "Оглушение", "Молчание") могут блокировать использование определенных или всех способностей. Abilities может подписаться на эти события, чтобы временно запретить использование способностей.
# StatsChangedEvent: В будущем, если появятся способности, которые разблокируются при достижении определенного значения характеристики (например, "Ярость" при низком HP), Abilities могло бы подписаться на изменение статов для проверки таких условий.