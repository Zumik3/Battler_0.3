# game/entities/player.py
"""Класс игрока (персонажа, управляемого игроком)."""
from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING
from game.config import get_config
from game.entities.character import Character
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
        is_player: bool = True,
    ):
        # Сохраняем данные класса
        self.base_stats_dict = base_stats_dict
        self.growth_rates_dict = growth_rates_dict
        self.class_icon = class_icon
        self.class_icon_color = class_icon_color if class_icon_color is not None else 0

        # Инициализируем систему опыта
        self.exp_calculator = exp_calculator if exp_calculator else SimpleExperienceCalculator()
        self.level_up_handler = level_up_handler if level_up_handler else SimpleLevelUpHandler()
        self.exp = 0
        self.exp_to_next_level = 0

        # Создаем фабрики по умолчанию если не предоставлены
        if stats_factory is None:
            stats_factory = self.get_base_stats
        if attributes_factory is None:
            attributes_factory = self._attributes_factory

        # Вызываем конструктор родительского класса
        super().__init__(
            name=name,
            role=role,
            level=level,
            is_player=is_player,
            stats_factory=stats_factory,
            attributes_factory=attributes_factory,
            ability_manager_factory=ability_manager_factory,
            status_effect_manager_factory=status_effect_manager_factory,
        )
        
        # Рассчитываем опыт для следующего уровня
        self.calculate_exp_for_next_level()

    # ==================== Вспомогательные методы для фабрик ====================
    def _attributes_factory(self, character: 'CharacterType') -> Attributes:
        """Фабрика для создания атрибутов."""
        return self.calculate_attributes()

    # ==================== Абстрактные методы ====================
    def get_base_stats(self) -> Stats:
        """Возвращает базовые характеристики персонажа."""
        stats = SimpleStats()
        # Масштабируем базовые характеристики в соответствии с уровнем
        level_multiplier = self.level * 0.1
        stats.strength = int(self.base_stats_dict.get('strength', 10) * 
                           (1 + level_multiplier * self.growth_rates_dict.get('strength', 1.0)))
        stats.agility = int(self.base_stats_dict.get('agility', 10) * 
                          (1 + level_multiplier * self.growth_rates_dict.get('agility', 1.0)))
        stats.intelligence = int(self.base_stats_dict.get('intelligence', 10) * 
                               (1 + level_multiplier * self.growth_rates_dict.get('intelligence', 1.0)))
        stats.vitality = int(self.base_stats_dict.get('vitality', 10) * 
                           (1 + level_multiplier * self.growth_rates_dict.get('vitality', 1.0)))
        return stats

    def calculate_attributes(self) -> Attributes:
        """Вычисляет атрибуты персонажа на основе его характеристик и уровня."""
        return SimpleAttributes(self, self.stats)

    # ==================== Уровень и характеристики ====================
    def level_up(self) -> List[Dict[str, Any]]:
        """
        Повышает уровень персонажа.
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

# ==================== Вспомогательные классы ====================

class SimpleStats:
    """Простая реализация базовых характеристик."""
    def __init__(self):
        self.strength = 0
        self.agility = 0
        self.intelligence = 0
        self.vitality = 0

# game/entities/player.py (обновленный фрагмент)
class SimpleAttributes:
    """Простая реализация производных атрибутов."""
    def __init__(self, character: 'Character', stats: Stats):
        self.character = character
        self.stats = stats
        config = get_config()
        
        # Расчет производных атрибутов с использованием настроек
        self.max_hp = config.character.base_max_hp + (stats.vitality * config.character.hp_per_vitality)
        self.max_energy = config.character.base_max_energy + (stats.intelligence * config.character.energy_per_intelligence)
        self.attack_power = stats.strength * config.character.attack_per_strength
        self.defense = int(stats.agility * config.character.defense_per_agility)

class SimpleExperienceCalculator:
    """Простой калькулятор опыта для следующего уровня."""
    def calculate_exp_for_next_level(self, current_level: int) -> int:
        """Рассчитывает опыт, необходимый для достижения следующего уровня."""
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