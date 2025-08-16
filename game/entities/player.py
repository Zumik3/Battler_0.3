# game/entities/player.py
"""Класс игрока (персонажа, управляемого игроком)."""
from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING
from game.entities.character import Character, SimpleStats, SimpleAttributes # Импортируем вспомогательные классы
from game.protocols import (
    Stats,
    Attributes,
    AbilityManagerProtocol,
    StatusEffectManagerProtocol,
    ExperienceCalculatorProtocol,
    LevelUpHandlerProtocol
)

if TYPE_CHECKING:
    from game.entities.character import Character as CharacterType

# - Фабричная функция для создания игрока из JSON -
def create_player_from_data(
    name: str,
    role: str,
    level: int = 1,
    data_directory: str = "game/data/characters/player_classes"
) -> Optional['Player']:
    """
    Создает объект Player на основе данных из JSON файла.

    Args:
        name: Имя персонажа.
        role: Внутренний идентификатор класса (должен совпадать с именем .json файла).
        level: Начальный уровень.
        data_directory: Путь к директории с JSON файлами.

    Returns:
        Объект Player или None, если данные не могут быть загружены.
    """
    try:
        from game.data.character_loader import load_player_class_data
    except ImportError as e:
        print(f"Ошибка импорта character_loader внутри create_player_from_data: {e}")
        return None

    data = load_player_class_data(role, data_directory)
    if not data:
        print(f"Не удалось загрузить данные для класса '{role}'")
        return None

    try:
        player = Player(
            name=name,
            role=data['role'],
            base_stats_dict=data['base_stats'],
            growth_rates_dict=data['growth_rates'],
            class_icon=data.get('class_icon', '?'),
            class_icon_color=data.get('class_icon_color'),
            level=level,
        )
        return player
    except Exception as e:
        print(f"Ошибка создания персонажа {name} класса {role}: {e}")
        import traceback
        traceback.print_exc()
        return None

# --- Основной класс игрока ---

class Player(Character):
    """Класс для всех игроков (персонажей, управляемых игроком)."""

    def __init__(
        self, 
        name: str, 
        role: str,
        # Параметры для системы уровней/опыта
        base_stats_dict: Dict[str, int],
        growth_rates_dict: Dict[str, float],
        class_icon: str = "?",
        class_icon_color: Optional[int] = None,
        level: int = 1,
        # Внедрение зависимостей через конструктор
        stats_factory: Optional[Callable[[], Stats]] = None, 
        attributes_factory: Optional[Callable[['CharacterType'], Attributes]] = None,
        ability_manager_factory: Optional[Callable[['CharacterType'], AbilityManagerProtocol]] = None,
        status_effect_manager_factory: Optional[Callable[['CharacterType'], StatusEffectManagerProtocol]] = None,
        exp_calculator: Optional[ExperienceCalculatorProtocol] = None,
        level_up_handler: Optional[LevelUpHandlerProtocol] = None,
        # is_player: bool = True, # Устанавливается автоматически
    ):
        # --- Атрибуты, специфичные для игрока ---
        self.class_icon = class_icon
        self.class_icon_color = class_icon_color if class_icon_color is not None else 0

        # Инициализируем систему опыта
        self.exp_calculator = exp_calculator if exp_calculator else SimpleExperienceCalculator()
        self.level_up_handler = level_up_handler if level_up_handler else SimpleLevelUpHandler()
        self.exp = 0
        self.exp_to_next_level = 0
        # --- Конец специфичных атрибутов ---

        # Вызываем конструктор родительского класса
        # Передаем все необходимые данные, включая base_stats_dict и growth_rates_dict
        super().__init__(
            name=name,
            role=role,
            base_stats_dict=base_stats_dict,
            growth_rates_dict=growth_rates_dict,
            level=level,
            is_player=True, # Всегда True для игрока
            stats_factory=stats_factory, # Может быть None, будет использована реализация по умолчанию из Character
            attributes_factory=attributes_factory, # Может быть None, будет использована реализация по умолчанию из Character
            ability_manager_factory=ability_manager_factory,
            status_effect_manager_factory=status_effect_manager_factory,
        )
        
        # Рассчитываем опыт для следующего уровня
        self.calculate_exp_for_next_level()

    # ==================== Уровень и характеристики (расширение) ====================
    # Переопределяем level_up, чтобы добавить логику опыта
    def level_up(self) -> List[Dict[str, Any]]:
        """
        Повышает уровень персонажа (игрока).
        Возвращает список сообщений/результатов.
        """
        # Вызываем родительский метод level_up
        results = super().level_up()
        
        # Пересчитываем опыт для следующего уровня
        self.calculate_exp_for_next_level()
        
        return results

    # ==================== Свойства ====================
    @property
    def experience_to_next_level(self) -> int:
        """Получение опыта, необходимого для следующего уровня."""
        return self.exp_to_next_level

    # ==================== Система опыта ====================
    def calculate_exp_for_next_level(self) -> None:
        """
        Рассчитывает количество опыта, необходимого для следующего уровня.
        """
        self.exp_to_next_level = self.exp_calculator.calculate_exp_for_next_level(self.level)

    def gain_experience(self, exp_amount: int) -> List[Dict[str, Any]]:
        """
        Добавляет опыт игроку и проверяет на повышение уровня.
        Возвращает список сообщений/результатов.
        """
        results = []
        self.exp += exp_amount
        results.append({
            "type": "exp_gained",
            "character": self.name,
            "exp_amount": exp_amount,
            "total_exp": self.exp
        })

        # Проверяем, достаточно ли опыта для повышения уровня
        while self.exp >= self.exp_to_next_level:
            # Сбрасываем опыт, использованный для повышения уровня
            self.exp -= self.exp_to_next_level
            
            # Повышаем уровень
            level_up_results = self.level_up()
            results.extend(level_up_results)
            
            # Дополнительная обработка повышения уровня
            handler_results = self.level_up_handler.handle_level_up(self)
            results.extend(handler_results)
            
            # Пересчитываем опыт для следующего уровня
            self.calculate_exp_for_next_level()

        return results

# ==================== Вспомогательные классы (специфичные для игрока) ====================

class SimpleExperienceCalculator:
    """Простой калькулятор опыта для следующего уровня."""
    def calculate_exp_for_next_level(self, current_level: int) -> int:
        """Рассчитывает опыт, необходимый для достижения следующего уровня."""
        from game.config import get_config # Локальный импорт для избежания циклических зависимостей на уровне модуля
        config = get_config()
        return int(config.experience.formula_base * (current_level ** config.experience.formula_multiplier))

class SimpleLevelUpHandler:
    """Простой обработчик повышения уровня."""
    def handle_level_up(self, character: 'Character') -> List[Dict[str, Any]]:
        """Обработать повышение уровня и вернуть список результатов."""
        results = []
        old_hp = character.hp
        character.hp = character.attributes.max_hp
        hp_restored = character.hp - old_hp
        
        old_energy = character.energy
        character.energy = character.attributes.max_energy
        energy_restored = character.energy - old_energy
        
        results.append({
            "type": "level_up_heal",
            "character": character.name,
            "hp_restored": hp_restored,
            "energy_restored": energy_restored
        })
        
        return results
