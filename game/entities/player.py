# game/entities/player.py
"""Класс игрока (персонажа, управляемого игроком)."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, TYPE_CHECKING
from game import config
from game.entities.character import Character, CharacterConfig, SimpleStats, SimpleAttributes # Импортируем вспомогательные классы
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

@dataclass
class PlayerConfig(CharacterConfig):
    is_player: bool = field(default=True)
    exp_calculator: Optional[ExperienceCalculatorProtocol] = None
    level_up_handler: Optional[LevelUpHandlerProtocol] = None
    

# - Фабричная функция для создания игрока из JSON -
def create_player_from_data(
    role: str,
    name: str,
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

    config_data = load_player_class_data(role, data_directory)
    if not config_data:
        print(f"Не удалось загрузить данные для класса '{role}'")
        return None

    try:
        config = PlayerConfig(**config_data)
        config.name = name if name else config.name
        return Player(config)

    except Exception as e:
        print(f"Ошибка создания персонажа {name} класса {role}: {e}")
        import traceback
        traceback.print_exc()
        return None

# --- Основной класс игрока ---

class Player(Character):
    """Класс для всех игроков (персонажей, управляемых игроком)."""

    def __init__(self, config: PlayerConfig):

        super().__init__(config=config)

        # Инициализируем систему опыта
        self.exp_calculator = config.exp_calculator if config.exp_calculator else SimpleExperienceCalculator()
        self.level_up_handler = config.level_up_handler if config.level_up_handler else SimpleLevelUpHandler()
        self.exp = 0
        self.exp_to_next_level = 0
        
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
