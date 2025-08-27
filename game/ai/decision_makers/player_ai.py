# game/ai/decision_makers/player_ai.py

import random
from typing import TYPE_CHECKING, Iterable, List, Tuple
from game.ai.ai_decision_maker import AIDecisionMaker

if TYPE_CHECKING:
    from game.entities.character import Character

class PlayerAI(AIDecisionMaker):
    """ИИ для игрока, использующий систему приоритетов."""

    def choose_action(
        self, 
        character: 'Character', 
        allies: Iterable['Character'], 
        enemies: Iterable['Character']
    ) -> Tuple[str, List['Character']]:
        """Выбирает действие на основе приоритетов."""
        
        # Получаем доступные способности
        available_abilities = character.abilities.get_available_abilities() if character.abilities else []
        if not available_abilities:
            return ("", [])
            
        alive_enemies = [e for e in enemies if e.is_alive()]
        if not alive_enemies:
            return ("", [])
            
        # Приоритет 1: Добивание слабых врагов
        action = self._try_finish_enemies(character, available_abilities, alive_enemies)
        if action:
            return action
            
        # Приоритет 2: Использование АоЕ по группе врагов
        action = self._try_aoe_attack(character, available_abilities, alive_enemies)
        if action:
            return action
            
        # Приоритет 3: Сильная одиночная атака
        action = self._try_strong_attack(character, available_abilities, alive_enemies)
        if action:
            return action
            
        # Приоритет 4: Базовая атака
        action = self._try_basic_attack(character, available_abilities, alive_enemies)
        if action:
            return action
            
        # Если ничего не подошло, выбираем случайно
        return self._choose_random_action(available_abilities, alive_enemies)

    def _try_finish_enemies(self, character: 'Character', 
        abilities: List[str], 
        enemies: List['Character']
        ) -> Tuple[str, List['Character']] | None:
        """Пытается добить врагов с низким HP."""
        # Ищем врагов с HP < 20%
        for enemy in enemies:
            if self._is_low_health(enemy, threshold=0.2):
                # Ищем подходящую способность для добивания
                finish_abilities = [a for a in abilities if self._is_damage_ability(a)]
                if finish_abilities:
                    return (random.choice(finish_abilities), [enemy])
        return None

    def _try_aoe_attack(self, character: 'Character', 
        abilities: List[str], 
        enemies: List['Character']
        ) -> Tuple[str, List['Character']] | None:
        """Пытается использовать АоЕ по группе врагов."""
        # Если врагов 2 или больше, ищем АоЕ способности
        if len(enemies) >= 2:
            aoe_abilities = [a for a in abilities if self._is_aoe_ability(a)]
            if aoe_abilities:
                # Используем АоЕ по всем врагам
                return (random.choice(aoe_abilities), enemies[:3])  # до 3 целей
        return None

    def _try_strong_attack(self, character: 'Character', 
        abilities: List[str], 
        enemies: List['Character']
        ) -> Tuple[str, List['Character']] | None:
        """Пытается использовать сильную одиночную атаку."""
        strong_abilities = [a for a in abilities if self._is_strong_attack(a)]
        if strong_abilities:
            target = random.choice(enemies)
            return (random.choice(strong_abilities), [target])
        return None

    def _try_basic_attack(self, character: 'Character', 
        abilities: List[str], 
        enemies: List['Character']) -> Tuple[str, List['Character']] | None:
        """Пытается использовать базовую атаку."""
        if "BasicAttack" in abilities:
            target = random.choice(enemies)
            return ("BasicAttack", [target])
        return None

    def _choose_random_action(self, abilities: List[str], enemies: List['Character']) -> Tuple[str, List['Character']]:
        """Выбирает случайное действие."""
        if abilities and enemies:
            ability = random.choice(abilities)
            target = random.choice(enemies)
            return (ability, [target])
        return ("", [])

    # --- Вспомогательные методы ---
    def _is_low_health(self, character: 'Character', threshold: float = 0.2) -> bool:
        """Проверяет, имеет ли персонаж низкий уровень здоровья."""
        if not character.health:
            return False
        current = getattr(character.health, 'health', 0)
        max_hp = getattr(character.health, 'max_health', 1)
        return max_hp > 0 and (current / max_hp) < threshold

    def _is_damage_ability(self, ability_name: str) -> bool:
        """Проверяет, является ли способность атакующей."""
        damage_keywords = ["attack", "strike", "hit", "slash", "fire", "ice", "bolt"]
        return any(keyword in ability_name.lower() for keyword in damage_keywords)

    def _is_aoe_ability(self, ability_name: str) -> bool:
        """Проверяет, является ли способность АоЕ."""
        aoe_keywords = ["aoe", "blast", "nova", "wave", "storm", "rain"]
        return any(keyword in ability_name.lower() for keyword in aoe_keywords)

    def _is_strong_attack(self, ability_name: str) -> bool:
        """Проверяет, является ли способность сильной атакой."""
        strong_keywords = ["power", "strong", "heavy", "mighty", "crushing"]
        return any(keyword in ability_name.lower() for keyword in strong_keywords)