# game/entities/properties/abilities.py
"""
Свойство способностей персонажа.
Управляет списком доступных способностей персонажа и логикой их использования.
"""

from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING, Optional

# Импорты из других модулей проекта
from game.entities.properties.property import DependentProperty  # Или PublishingAndDependentProperty
from game.protocols import AbilityManagerProtocol
from game.systems.combat import ability_registry  # Предполагаем, что протокол уже определен

# Импорты для аннотаций типов
if TYPE_CHECKING:
    from game.entities.character import Character
    # Предполагаемые типы для реестра и способностей
    from game.protocols import AbilityRegistryProtocol 


@dataclass
class Abilities(DependentProperty, AbilityManagerProtocol):
    """
    Свойство для управления способностями персонажа.
    
    Атрибуты:
        abilities: Список имен доступных способностей.
        context: Контекст свойства, предоставляющий доступ к event_bus и character.
                 Также будет предоставлять доступ к ability_registry.
    """

    # Список имен способностей, доступных персонажу
    abilities: List[str] = field(default_factory=list)
    ability_registry: Optional['AbilityRegistryProtocol'] = None

    # Контекст уже есть в DependentProperty как self.context: 'PropertyContext'
    # Если нужно напрямую работать с GameContext или CharacterContext, можно добавить:
    # character_context: Optional['CharacterContext'] = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Инициализация свойства способностей."""
        super().__post_init__()
        
        # Подписки, если нужны
        # self._setup_subscriptions()

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

    def use_ability(self, ability_name: str, target: List['Character'], **kwargs) -> None:
        """
        Использует способность по имени.

        Args:
            ability_name: Название способности для использования.
            target: Список целей.
            **kwargs: Дополнительные аргументы.

        Returns:
            Список результатов действия (ActionResult).
        """
        # TODO: Реализовать логику использования способности
        # 1. Проверить, есть ли способность в списке доступных
        # 2. Получить фабрику из реестра (через context или character_context)
        # 3. Создать экземпляр Action
        # 4. Настроить Action (цель, параметры)
        # 5. Выполнить Action (_execute или execute)
        # 6. Вернуть результаты
        
        # Заглушка
        print(f"[Abilities] Использование способности '{ability_name}' не реализовано.")

    def get_available_abilities(self) -> List[str]:
        """
        Получить список имен доступных способностей.

        Returns:
            Список имен способностей.
        """
        return self.abilities.copy() # Возвращаем копию, чтобы не сломать внутренний список

    # Другие методы из протокола (update_cooldowns и т.д.) можно реализовать позже
    def update_cooldowns(self) -> None:
        """Обновить кулдауны способностей."""
        # TODO: Реализовать, если добавим систему кулдаунов

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