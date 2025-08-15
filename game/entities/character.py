# game/entities/character.py
"""Базовый класс персонажа в игре."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING
from game.protocols import (
    Stats, 
    Attributes,
    AbilityManagerProtocol, 
    StatusEffectManagerProtocol,
    Ability,
    StatusEffect
)

if TYPE_CHECKING:
    from game.entities.character import Character as CharacterType

# --- Основной класс персонажа ---

class Character(ABC):
    """Абстрактный базовый класс, представляющий персонажа в игре."""

    def __init__(
        self, 
        name: str, 
        role: str, 
        level: int = 1,
        is_player: bool = False,
        # Внедрение зависимостей через конструктор
        stats_factory: Optional[Callable[[], Stats]] = None, 
        attributes_factory: Optional[Callable[['CharacterType'], Attributes]] = None,
        ability_manager_factory: Optional[Callable[['CharacterType'], AbilityManagerProtocol]] = None,
        status_effect_manager_factory: Optional[Callable[['CharacterType'], StatusEffectManagerProtocol]] = None,
    ):
        self.name = name
        self.role = role
        self.level = level
        self.alive = True
        self.is_player = is_player

        # Безопасная инициализация характеристик
        if stats_factory:
            self.stats: Stats = stats_factory()
        
        if attributes_factory:
            self.attributes: Attributes = attributes_factory(self)
        
        # Инициализируем hp и энергию
        self.hp = self.attributes.max_hp
        self.energy = self.attributes.max_energy
        
        # Менеджеры (внедрение зависимостей)
        self._ability_manager: Optional[AbilityManagerProtocol] = None
        if ability_manager_factory:
            self._ability_manager = ability_manager_factory(self)
            
        self._status_manager: Optional[StatusEffectManagerProtocol] = None
        if status_effect_manager_factory:
            self._status_manager = status_effect_manager_factory(self)

    # ==================== Абстрактные методы ====================
    @abstractmethod
    def get_base_stats(self) -> Stats:
        """Возвращает базовые характеристики персонажа."""
        pass

    @abstractmethod
    def calculate_attributes(self) -> Attributes:
        """Вычисляет атрибуты персонажа на основе его характеристик и уровня."""
        pass

    # ==================== Уровень и характеристики ====================
    def level_up(self) -> List[Dict[str, Any]]:
        """
        Повышает уровень персонажа.
        Возвращает список сообщений/результатов.
        """
        self.level += 1
        
        # Сохраняем текущие проценты HP и энергии
        hp_ratio = self.hp / self.attributes.max_hp if self.attributes.max_hp > 0 else 1.0
        energy_ratio = self.energy / self.attributes.max_energy if self.attributes.max_energy > 0 else 1.0
        
        # Пересчитываем характеристики и атрибуты через абстрактные методы
        try:
            self.stats = self.get_base_stats()
            self.attributes = self.calculate_attributes()
        except NotImplementedError:
            # fallback если абстрактные методы не реализованы корректно
            pass
        
        # Обновляем текущие значения с учетом новых максимумов
        self.hp = max(1, int(self.attributes.max_hp * hp_ratio))
        self.energy = int(self.attributes.max_energy * energy_ratio)
        
        return [{"type": "level_up", "message": f"{self.name} достиг уровня {self.level}!"}]

    # ==================== Свойства ====================
    @property
    def ability_manager(self) -> Optional[AbilityManagerProtocol]:
        """Получение менеджера способностей."""
        return self._ability_manager

    @property
    def status_manager(self) -> Optional[StatusEffectManagerProtocol]:
        """Получение менеджера статус-эффектов."""
        return self._status_manager

    # ==================== Основные методы персонажа ====================
    def is_alive(self) -> bool:
        """Проверяет, жив ли персонаж."""
        return self.alive

    def get_level(self) -> int:
        """Возвращает уровень персонажа."""
        return self.level

    def on_death(self) -> List[Dict[str, Any]]:
        """
        Вызывается при смерти персонажа. 
        Возвращает список сообщений/результатов.
        """
        results = []
        
        # Очищаем все активные статус-эффекты
        if self._status_manager is not None:
            clear_results = self._status_manager.clear_all_effects()
            results.extend(clear_results)
        
        # Добавляем сообщение о смерти
        results.append({"type": "death", "message": f"{self.name} погибает!"})
        return results

    # ==================== Боевые методы ====================
    def take_damage(self, damage: int) -> List[Dict[str, Any]]:
        """
        Наносит урон персонажу, учитывая защиту.
        Возвращает список сообщений/результатов.
        """
        results = []
        # Учитываем защиту из attributes.defense
        actual_damage = max(0, damage - self.attributes.defense // 2)  # Может быть 0 урон
        actual_damage = max(1, actual_damage) if damage > 0 else 0  # Минимум 1 урон если был урон
        
        self.hp -= actual_damage
        results.append({
            "type": "damage_taken", 
            "target": self.name, 
            "damage": actual_damage,
            "hp_left": self.hp
        })
        
        if self.hp <= 0:
            self.hp = 0
            if self.alive:  # Проверяем, чтобы не вызывать on_death дважды
                self.alive = False
                death_results = self.on_death()
                results.extend(death_results)
                
        return results

    def take_heal(self, heal_amount: int) -> List[Dict[str, Any]]:
        """
        Исцеляет персонажа и возвращает список сообщений/результатов.
        """
        results = []
        old_hp = self.hp
        self.hp = min(self.attributes.max_hp, self.hp + heal_amount)
        actual_heal = self.hp - old_hp
        results.append({
            "type": "healed", 
            "target": self.name, 
            "heal_amount": actual_heal,
            "hp_now": self.hp
        })
        return results

    # ==================== Энергия ====================
    def restore_energy(self, amount: Optional[int] = None, percentage: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Восстанавливает энергию персонажа.
        :param amount: конкретное количество энергии для восстановления
        :param percentage: процент от максимальной энергии для восстановления
        Возвращает список сообщений/результатов.
        """
        results = []
        old_energy = self.energy
        
        if percentage is not None:
            restore_amount = int(self.attributes.max_energy * (percentage / 100.0))
            self.energy = min(self.attributes.max_energy, self.energy + restore_amount)
        elif amount is not None:
            self.energy = min(self.attributes.max_energy, self.energy + amount)
        else:
            self.energy = self.attributes.max_energy  # Полное восстановление
            
        actual_restore = self.energy - old_energy
        if actual_restore > 0:
            results.append({
                "type": "energy_restored", 
                "target": self.name, 
                "amount": actual_restore,
                "energy_now": self.energy
            })
            
        return results

    def spend_energy(self, amount: int) -> bool:
        """
        Тратит энергию персонажа.
        Возвращает True, если энергия была потрачена, иначе False.
        """
        if self.energy >= amount:
            self.energy -= amount
            return True
        return False

    # ==================== Способности ====================
    def add_ability(self, name: str, ability: Ability) -> None:
        """Добавляет способность персонажу."""
        if self._ability_manager:
            self._ability_manager.add_ability(name, ability)

    def get_available_abilities(self) -> List[str]:
        """Получает список доступных способностей."""
        if self._ability_manager:
            return self._ability_manager.get_available_abilities(self)
        return []

    def use_ability(self, name: str, targets: List['CharacterType'], **kwargs) -> List[Dict[str, Any]]:
        """
        Использует способность по имени.
        Возвращает список сообщений/результатов от способности и менеджера.
        """
        results = []
        if self._ability_manager:
            ability_result = self._ability_manager.use_ability(name, self, targets, **kwargs)
            if ability_result:
                if isinstance(ability_result, list):
                    results.extend(ability_result)
                else:
                    results.append(ability_result)
        return results

    def update_ability_cooldowns(self) -> None:
        """Обновляет кулдауны способностей в конце раунда."""
        if self._ability_manager:
            self._ability_manager.update_cooldowns()

    # ==================== Статус-эффекты ====================
    def add_status_effect(self, effect: StatusEffect) -> List[Dict[str, Any]]:
        """Добавляет статус-эффект персонажу. Возвращает результат от менеджера."""
        if self._status_manager:
            return [self._status_manager.add_effect(effect)]
        return []

    def remove_status_effect(self, effect_name: str) -> List[Dict[str, Any]]:
        """Удаляет статус-эффект по имени. Возвращает результат."""
        results = []
        if self._status_manager:
            success = self._status_manager.remove_effect(effect_name)
            if success:
                results.append({"type": "effect_removed", "effect": effect_name, "target": self.name})
            else:
                results.append({"type": "error", "message": f"Эффект {effect_name} не найден у {self.name}"})
        return results

    def update_status_effects(self) -> List[Dict[str, Any]]:
        """Обновляет все активные статус-эффекты. Возвращает список результатов."""
        if self._status_manager:
            return self._status_manager.update_effects()
        return []

    def has_status_effect(self, effect_name: str) -> bool:
        """Проверяет, есть ли у персонажа определенный статус-эффект."""
        if self._status_manager:
            return self._status_manager.has_effect(effect_name)
        return False

    def get_active_status_effects(self) -> List[StatusEffect]:
        """Возвращает список всех активных статус-эффектов."""
        if self._status_manager:
            return self._status_manager.get_all_effects()
        return []