# game/systems/combat/ability_registry.py
"""Реестр способностей игры."""

from typing import Dict, Callable, TYPE_CHECKING, Optional
from game.protocols import AbilityRegistryProtocol

# Импорты базовых способностей для автоматической регистрации
from game.actions.basic_attack import BasicAttack
from game.actions.basic_heal import BasicHeal

if TYPE_CHECKING:
    from game.entities.character import Character
    from game.actions.action import Action


class AbilityRegistry(AbilityRegistryProtocol):
    """
    Реализация реестра способностей.
    Хранит отображение имя_способности -> фабричная_функция.
    Автоматически регистрирует встроенные способности при инициализации.
    """

    # Внутренний словарь для автоматической регистрации встроенных способностей
    # Формат: {"имя_способности": (класс_способности, описание)}
    _BUILTIN_ABILITIES = {
        "BasicAttack": (BasicAttack, "Базовая физическая атака"),
        "BasicHeal": (BasicHeal, "Базовое лечение"), 
        # ... другие способности будут добавляться сюда
    }

    def __init__(self) -> None:
        """Инициализирует реестр способностей и автоматически регистрирует встроенные способности."""
        # Словарь: имя способности -> фабрика (Callable, создающая Action из Character)
        self._registry: Dict[str, Callable[['Character'], 'Action']] = {}
        
        # Автоматическая регистрация встроенных способностей
        self._register_builtin_abilities()

    def _register_builtin_abilities(self) -> None:
        """Регистрирует все встроенные способности из _BUILTIN_ABILITIES."""
        for name, (action_class, _) in self._BUILTIN_ABILITIES.items():
            # Явно аннотируем тип фабричной функции для mypy
            factory: Callable[['Character'], 'Action'] = lambda char, cls=action_class: cls(char)
            self.register(name, factory)

    def register(self, name: str, factory: Callable[['Character'], 'Action']) -> None:
        """
        Регистрирует новую способность в реестре.

        Args:
            name: Имя способности (должно совпадать с именем в JSON конфигурации персонажа).
            factory: Функция или callable, который принимает объект Character (источник)
                     и возвращает экземпляр Action.
        """
        if name in self._registry:
            # Можно логировать предупреждение о перезаписи
            print(f"[AbilityRegistry] Предупреждение: Способность '{name}' уже зарегистрирована. Перезапись.")
        self._registry[name] = factory

    def get_factory(self, ability_name: str) -> Callable[['Character'], 'Action']:
        """
        Получает зарегистрированную фабрику для создания способности по имени.

        Args:
            ability_name: Имя способности для поиска.

        Returns:
            Функция-фабрика, создающая экземпляр Action.

        Raises:
            KeyError: Если способность с таким именем не найдена в реестре.
        """
        if ability_name not in self._registry:
            raise KeyError(f"Способность '{ability_name}' не найдена в реестре.")
        return self._registry[ability_name]

    def is_registered(self, ability_name: str) -> bool:
        """
        Проверяет, зарегистрирована ли способность с заданным именем.

        Args:
            ability_name: Имя способности для проверки.

        Returns:
            True, если способность зарегистрирована, иначе False.
        """
        return ability_name in self._registry

    def get_ability_info(self, ability_name: str) -> Optional[tuple[type['Action'], str]]:
        """
        Получает информацию о способности из внутреннего словаря.

        Args:
            ability_name: Имя способности.

        Returns:
            Кортеж (класс_способности, описание) или None, если не найдена.
        """
        return self._BUILTIN_ABILITIES.get(ability_name)
