# game/systems/combat/cooldown_manager.py
"""Менеджер кулдаунов для игровых способностей.

Отслеживает активные кулдауны для персонажей по именам способностей.
Предоставляет методы для проверки, применения и обновления кулдаунов.
"""

from typing import Dict, List, Optional, TYPE_CHECKING, Final

from game.events.combat import AbilityUsedEvent

# Импорты для аннотаций типов
if TYPE_CHECKING:
    from game.entities.character import Character
    from game.events.battle_events import RoundEndedEvent, BattleEndedEvent
    from game.systems.events.bus import IEventBus

class CooldownManager:
    """Менеджер для централизованного управления кулдаунами способностей."""

    def __init__(self, event_bus: 'IEventBus') -> None:
        """
        Инициализирует менеджер кулдаунов и настраивает подписки на события.

        Args:
            event_bus: Шина событий для автоматической подписки.
        """
        # Структура: id(character) -> {ability_name -> remaining_duration}
        self._cooldowns: Dict[int, Dict[str, int]] = {}
        self._setup_subscriptions(event_bus)

    def _setup_subscriptions(self, event_bus: 'IEventBus') -> None:
        """Настраивает подписки на события."""
        from game.events.battle_events import RoundEndedEvent, BattleEndedEvent
        event_bus.subscribe(None, RoundEndedEvent, self._on_round_ended)
        event_bus.subscribe(None, BattleEndedEvent, self._on_battle_ended)
        event_bus.subscribe(None, AbilityUsedEvent, self._on_ability_used)

    def _on_round_ended(self, event: 'RoundEndedEvent') -> None:
        """
        Обработчик события окончания раунда.
        Обновляет кулдауны для всех персонажей.
        """
        self.update_cooldowns()

    def _on_battle_ended(self, event: 'BattleEndedEvent') -> None:
        """
        Обработчик события окончания боя.
        Очищает все активные кулдауны.
        """
        self.clear_all_cooldowns()

    def _on_ability_used(self, event: 'AbilityUsedEvent') -> None:
        if event.cooldown > 0 and event.character:
            self.apply_cooldown(event.character, event.ability_name, event.cooldown)

    def is_on_cooldown(self, character: 'Character', ability_name: str) -> bool:
        """
        Проверяет, находится ли способность персонажа на кулдауне.

        Args:
            character: Персонаж, для которого проверяется кулдаун.
            ability_name: Имя способности.

        Returns:
            True, если способность на кулдауне, иначе False.
        """
        char_id = id(character)
        char_cooldowns = self._cooldowns.get(char_id, {})
        return ability_name in char_cooldowns and char_cooldowns[ability_name] > 0

    def apply_cooldown(self, character: 'Character', ability_name: str, duration: int) -> None:
        """
        Применяет или сбрасывает кулдаун для способности персонажа.

        Args:
            character: Персонаж, для которого устанавливается кулдаун.
            ability_name: Имя способности.
            duration: Длительность кулдауна в ходах.
        """
        char_id = id(character)
        if char_id not in self._cooldowns:
            self._cooldowns[char_id] = {}
        
        # Устанавливаем или сбрасываем кулдаун
        self._cooldowns[char_id][ability_name] = duration

    def get_remaining_cooldown(self, character: 'Character', ability_name: str) -> int:
        """
        Получает оставшееся время кулдауна для способности персонажа.

        Args:
            character: Персонаж.
            ability_name: Имя способности.

        Returns:
            Оставшееся время кулдауна в ходах. 0, если кулдаун не активен.
        """
        char_id = id(character)
        char_cooldowns = self._cooldowns.get(char_id, {})
        return char_cooldowns.get(ability_name, 0)

    def update_cooldowns(self) -> None:
        """
        Обновляет (уменьшает) кулдауны для всех персонажей на 1 ход.

        Этот метод должен вызываться в конце общего раунда боя.
        """
        characters_to_remove = []
        for char_id, abilities in self._cooldowns.items():
            abilities_to_remove = []
            for ability_name, remaining in abilities.items():
                # Уменьшаем кулдаун, но не ниже 0
                self._cooldowns[char_id][ability_name] = max(0, remaining - 1)
                # Если кулдаун завершен, помечаем для удаления
                if self._cooldowns[char_id][ability_name] == 0:
                    abilities_to_remove.append(ability_name)
            
            # Удаляем завершенные кулдауны конкретного персонажа
            for ability_name in abilities_to_remove:
                del self._cooldowns[char_id][ability_name]
            
            # Если у персонажа не осталось активных кулдаунов, 
            # помечаем его словарь для удаления
            if not self._cooldowns[char_id]:
                characters_to_remove.append(char_id)
        
        # Удаляем записи для персонажей без активных кулдаунов
        for char_id in characters_to_remove:
            del self._cooldowns[char_id]

    def remove_cooldown(self, character: 'Character', ability_name: str) -> bool:
        """
        Принудительно убирает кулдаун для способности персонажа.

        Args:
            character: Персонаж.
            ability_name: Имя способности.

        Returns:
            True, если кулдаун был успешно удален, иначе False.
        """
        char_id = id(character)
        if char_id in self._cooldowns and ability_name in self._cooldowns[char_id]:
            del self._cooldowns[char_id][ability_name]
            # Удаляем пустой словарь персонажа, если нужно
            if not self._cooldowns[char_id]:
                del self._cooldowns[char_id]
            return True
        return False

    def clear_all_cooldowns(self) -> None:
        """
        Полностью очищает все активные кулдауны для всех персонажей.
        
        Этот метод должен вызываться в конце боя.
        """
        self._cooldowns.clear()

    def get_all_cooldowns(self, character: 'Character') -> Dict[str, int]:
        """
        Получает словарь всех активных кулдаунов персонажа.

        Args:
            character: Персонаж.

        Returns:
            Словарь {имя_способности: оставшееся_время}.
        """
        char_id = id(character)
        return self._cooldowns.get(char_id, {}).copy()

    def get_ready_abilities(self, character: 'Character', all_abilities: List[str]) -> List[str]:
        """
        Фильтрует список способностей, возвращая только те, которые не находятся на кулдауне.
        
        Args:
            character: Персонаж, для которого проверяются кулдауны.
            all_abilities: Полный список имен способностей для проверки.
            
        Returns:
            Список имен способностей, которые не на кулдауне.
        """
        ready_abilities = []
        for ability_name in all_abilities:
            if not self.is_on_cooldown(character, ability_name):
                ready_abilities.append(ability_name)
        return ready_abilities


# Единственный экземпляр менеджера кулдаунов на всю игру
_cooldown_manager_instance: Optional[CooldownManager] = None

def get_cooldown_manager(event_bus: Optional['IEventBus'] = None) -> CooldownManager:
    """
    Получает глобальный экземпляр CooldownManager (синглтон).
                   
    Args:
        event_bus: Шина событий для инициализации синглтона при первом вызове.
                   Игнорируется при последующих вызовах.
                   
    Returns:
        Глобальный экземпляр CooldownManager.
        
    Raises:
        RuntimeError: Если синглтон еще не инициализирован и event_bus не предоставлен.
    """
    global _cooldown_manager_instance
    if _cooldown_manager_instance is None:
        if event_bus is None:
            raise RuntimeError("CooldownManager синглтон еще не инициализирован. Необходимо предоставить event_bus при первом вызове.")
        _cooldown_manager_instance = CooldownManager(event_bus)
    return _cooldown_manager_instance
