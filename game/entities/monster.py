# game/entities/monster.py
"""Класс монстра (персонажа, НЕ управляемого игроком)."""
from typing import Dict, Any, Optional, Callable, TYPE_CHECKING
from game.entities.character import Character, SimpleStats, SimpleAttributes # Импортируем вспомогательные классы
from game.protocols import (
    Stats,
    Attributes,
    AbilityManagerProtocol,
    StatusEffectManagerProtocol
)

if TYPE_CHECKING:
    from game.entities.character import Character as CharacterType

# - Фабричная функция для создания монстра из JSON -
def create_monster_from_data(
    name: str,
    role: str,
    level: int = 1,
    data_directory: str = "game/data/characters/monster_classes"
) -> Optional['Monster']:
    """
    Создает объект Monster на основе данных из JSON файла.

    Args:
        name: Имя монстра.
        role: Внутренний идентификатор класса (должен совпадать с именем .json файла).
        level: Начальный уровень.
        data_directory: Путь к директории с JSON файлами.

    Returns:
        Объект Monster или None, если данные не могут быть загружены.
    """
    try:
        from game.data.character_loader import load_monster_class_data
    except ImportError as e:
        print(f"Ошибка импорта character_loader внутри create_monster_from_data: {e}")
        return None

    data = load_monster_class_data(role, data_directory)
    if not data:
        print(f"Не удалось загрузить данные для класса монстра '{role}'")
        return None

    try:
        monster = Monster(
            name=name,
            role=data['role'],
            base_stats_dict=data['base_stats'],
            growth_rates_dict=data.get('growth_rates', {}), # growth_rates может отсутствовать
            class_icon=data.get('class_icon', '?'),
            class_icon_color=data.get('class_icon_color'),
            level=level,
        )
        return monster
    except Exception as e:
        print(f"Ошибка создания монстра {name} класса {role}: {e}")
        import traceback
        traceback.print_exc()
        return None

# --- Основной класс монстра ---

class Monster(Character):
    """Класс для всех монстров (персонажей, НЕ управляемых игроком)."""

    def __init__(
        self, 
        name: str, 
        role: str,
        # Параметры для системы уровней (без опыта)
        base_stats_dict: Dict[str, int],
        growth_rates_dict: Dict[str, float],
        class_icon: str = "?",
        class_icon_color: Optional[int] = None,
        level: int = 1,
        # Внедрение зависимостей через конструктор
        stats_factory: Optional[Callable[[], Stats]] = None, 
        attributes_factory: Optional[Callable[['CharacterType'], Attributes]] = None,
        ability_manager_factory: Optional[Callable[['CharacterType'], AbilityManagerProtocol]] = None,
        status_effect_manager_factory: Optional[Callable[['CharacterType'], StatusEffectManagerProtocol]] = None
    ):
        # --- Атрибуты, специфичные для монстра (если будут) ---
        self.class_icon = class_icon # Можно убрать, если не используется
        self.class_icon_color = class_icon_color if class_icon_color is not None else 0 # Можно убрать, если не используется
        # --- Конец специфичных атрибутов ---

        # Вызываем конструктор родительского класса
        # Передаем все необходимые данные, включая base_stats_dict и growth_rates_dict
        # is_player принудительно устанавливаем в False
        super().__init__(
            name=name,
            role=role,
            base_stats_dict=base_stats_dict,
            growth_rates_dict=growth_rates_dict,
            level=level,
            is_player=False, # Всегда False для монстра
            stats_factory=stats_factory, # Может быть None, будет использована реализация по умолчанию из Character
            attributes_factory=attributes_factory, # Может быть None, будет использована реализация по умолчанию из Character
            ability_manager_factory=ability_manager_factory,
            status_effect_manager_factory=status_effect_manager_factory,
        )

