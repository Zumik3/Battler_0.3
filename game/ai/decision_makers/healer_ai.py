# game/ai/decision_makers/healer_ai.py
"""ИИ для класса лекаря, ориентированный на поддержку и лечение."""

import random
from typing import TYPE_CHECKING, Iterable, List, Tuple
from game.ai.ai_decision_maker import AIDecisionMaker

if TYPE_CHECKING:
    from game.entities.character import Character


class HealerAI(AIDecisionMaker):
    """ИИ для игрока-лекаря, использующий систему приоритетов, ориентированную на поддержку."""

    def choose_action(
        self,
        character: 'Character',
        allies: Iterable['Character'],
        enemies: Iterable['Character']
    ) -> Tuple[str, List['Character']]:
        """Выбирает действие на основе приоритетов, характерных для лекаря."""

        # Получаем доступные способности
        available_abilities = character.abilities.get_available_abilities() if character.abilities else []
        if not available_abilities:
            return ("", [])

        alive_allies = [a for a in allies if a.is_alive()]
        alive_enemies = [e for e in enemies if e.is_alive()]

        if not alive_allies: # На всякий случай
             return ("", [])

        # Приоритет 1: Лечение критически раненых союзников
        action = self._try_heal_critical_allies(character, available_abilities, alive_allies)
        if action:
            return action

        # Приоритет 2: Атака по врагам с низким HP (добивание)
        if alive_enemies:
            action = self._try_finish_enemies(character, available_abilities, alive_enemies)
            if action:
                return action

        # Приоритет 3: Профилактическое лечение союзников
        action = self._try_heal_allies(character, available_abilities, alive_allies)
        if action:
            return action

        # Приоритет 5: Базовая атака
        if alive_enemies:
            action = self._try_basic_attack(character, available_abilities, alive_enemies)
            if action:
                return action

        # Если ничего не подошло, выбираем случайно (на случай, если остались только вспомогательные способности)
        if alive_enemies:
            return self._choose_random_action(available_abilities, alive_enemies)
        else:
            # Если врагов нет, можно выбрать случайного союзника (например, для бафов, если бы они были)
            random_ally = random.choice(alive_allies)
            if available_abilities:
                 ability = random.choice(available_abilities)
                 # Предполагаем, что цель может быть союзником или врагом. Для универсальности возьмем одного союзника.
                 # В реальной игре нужно уточнить, какие способности на кого действуют.
                 return (ability, [random_ally])
        return ("", [])


    def _try_heal_critical_allies(self, character: 'Character',
        abilities: List[str],
        allies: List['Character']
    ) -> Tuple[str, List['Character']] | None:
        """Пытается лечить союзников с критически низким HP."""
        heal_abilities = [a for a in abilities if self._is_heal_ability(a)]
        if not heal_abilities:
            return None

        # Ищем союзников с HP < 30%
        critical_allies = [ally for ally in allies if self._is_low_health(ally, threshold=0.3)]
        if critical_allies:
            # Лечим первого попавшегося критически раненого
            target = critical_allies[0]
            # Выбираем самую сильную доступную лечебную способность
            heal_ability = max(heal_abilities, key=lambda a: self._get_heal_potential(a)) # Простая оценка
            return (heal_ability, [target])
        return None

    def _try_heal_allies(self, character: 'Character',
        abilities: List[str],
        allies: List['Character']
    ) -> Tuple[str, List['Character']] | None:
        """Пытается лечить союзников с пониженным HP."""
        heal_abilities = [a for a in abilities if self._is_heal_ability(a)]
        if not heal_abilities:
            return None

        # Ищем союзников с HP < 60%
        wounded_allies = [ally for ally in allies if self._is_low_health(ally, threshold=0.6)]
        if wounded_allies:
            # Лечим первого попавшегося раненого
            target = wounded_allies[0]
            heal_ability = random.choice(heal_abilities) # Или выбрать наилучшую
            return (heal_ability, [target])
        return None

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
        damage_keywords = ["attack", "strike", "hit", "slash", "fire", "ice", "bolt", "missile"] # Добавил missile
        return any(keyword in ability_name.lower() for keyword in damage_keywords)

    def _is_heal_ability(self, ability_name: str) -> bool:
        """Проверяет, является ли способность лечебной."""
        heal_keywords = ["heal", "cure", "mend", "restore", "renew"]
        return any(keyword in ability_name.lower() for keyword in heal_keywords)

    def _is_strong_attack(self, ability_name: str) -> bool:
        """Проверяет, является ли способность сильной атакой."""
        strong_keywords = ["power", "strong", "heavy", "mighty", "crushing", "magic missile"] # Добавил magic missile как пример сильной атаки
        return any(keyword in ability_name.lower() for keyword in strong_keywords)

    def _get_heal_potential(self, ability_name: str) -> int:
        """Оценка потенциала лечения способности (для выбора наилучшей)."""
        # Это очень упрощенная оценка. В реальной игре можно было бы хранить базовые значения.
        heal_keywords = {
            "minor": 1,
            "lesser": 2,
            "basic": 2,
            "standard": 3,
            "greater": 4,
            "major": 5,
            "mass": 3 # Массовое, но на единицу меньше
        }
        # Проверяем ключевые слова в названии
        for keyword, value in heal_keywords.items():
             if keyword in ability_name.lower():
                 # Если массовое, потенциал выше, если цель одна
                 if "mass" in ability_name.lower():
                     return value # Предполагаем, что массовое лечение эффективнее для группы
                 return value * 2 # Удваиваем для одиночных целей
        return 1 # Базовое значение

    # def _is_aoe_ability(self, ability_name: str) -> bool:
    #     """Проверяет, является ли способность АоЕ."""
    #     # Для лекаря это может быть массовое лечение
    #     aoe_keywords = ["aoe", "blast", "nova", "wave", "storm", "rain", "mass"]
    #     return any(keyword in ability_name.lower() for keyword in aoe_keywords)