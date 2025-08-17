# game/entities/player.py
"""Класс игрока (персонажа, управляемого игроком)."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from game.entities.character import Character, CharacterConfig
from game.protocols import (
    ExperienceCalculatorProtocol,
    LevelUpHandlerProtocol
)
from game.systems.implementations import (
    SimpleExperienceCalculator, 
    SimpleLevelUpHandler
)
from game.systems.experience import ExperienceSystem, LevelingSystem
from game.results import ActionResult

if TYPE_CHECKING:
    from game.entities.character import Character as CharacterType


@dataclass
class PlayerConfig(CharacterConfig):
    """Конфигурация для создания игрока."""
    is_player: bool = field(default=True)
    exp_calculator: Optional[ExperienceCalculatorProtocol] = None
    level_up_handler: Optional[LevelUpHandlerProtocol] = None


def create_player_from_data(
    role: str,
    name: str,
    level: int = 1,
    data_directory: str = "game/data/characters/player_classes"
) -> Optional['Player']:
    """
    Создает объект Player на основе данных из JSON файла.

    Args:
        role: Внутренний идентификатор класса (должен совпадать с именем .json файла).
        name: Имя персонажа.
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


class Player(Character):
    """Класс для всех игроков (персонажей, управляемых игроком)."""

    def __init__(self, config: PlayerConfig):
        """
        Инициализирует игрока.

        Args:
            config: Конфигурация игрока.
        """
        super().__init__(config=config)

        # Инициализируем системы
        exp_calculator = config.exp_calculator or SimpleExperienceCalculator()
        level_up_handler = config.level_up_handler or SimpleLevelUpHandler()
        
        self.experience_system = ExperienceSystem(exp_calculator)
        self.leveling_system = LevelingSystem(level_up_handler)
        
        self.exp = 0
        self.exp_to_next_level = self.experience_system.calculate_exp_for_next_level(self.level)

    def level_up(self) -> List[ActionResult]:
        """
        Повышает уровень персонажа (игрока).

        Returns:
            Список сообщений/результатов повышения уровня.
        """
        # Вызываем родительский метод level_up
        results = super().level_up()
        
        # Пересчитываем опыт для следующего уровня
        self.exp_to_next_level = self.experience_system.calculate_exp_for_next_level(self.level)
        
        return results

    @property
    def experience_to_next_level(self) -> int:
        """Получение опыта, необходимого для следующего уровня."""
        return self.exp_to_next_level

    def gain_experience(self, exp_amount: int) -> List[ActionResult]:
        """
        Добавляет опыт игроку и проверяет на повышение уровня.

        Args:
            exp_amount: Количество получаемого опыта.

        Returns:
            Список результатов добавления опыта и возможного повышения уровня.
        """
        results: List[ActionResult] = []
        
        # Добавляем опыт
        self.exp += exp_amount
        exp_results = self.experience_system.add_experience(self, exp_amount)
        results.extend(exp_results)

        # Проверяем, достаточно ли опыта для повышения уровня
        while self.exp >= self.exp_to_next_level:
            # Сбрасываем опыт, использованный для повышения уровня
            self.exp -= self.exp_to_next_level
            
            # Повышаем уровень через родительский метод
            level_up_results = super().level_up()
            results.extend(level_up_results)
            
            # Дополнительная обработка повышения уровня
            level_results = self.leveling_system.try_level_up(self)
            results.extend(level_results)
            
            # Пересчитываем опыт для следующего уровня
            self.exp_to_next_level = self.experience_system.calculate_exp_for_next_level(self.level)

        return results