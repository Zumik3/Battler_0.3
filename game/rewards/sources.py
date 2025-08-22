# game/rewards/sources.py
"""Источники наград."""

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from game.entities.character import Character # Для типа награды
    from game.rewards.reward import Reward # Пока еще не создан, но будет

class RewardSource(ABC):
    """
    Абстрактный класс для источника наград.
    Источником может быть монстр, сундук, квест и т.д.
    """

    @abstractmethod
    def get_rewards(self) -> List['Reward']:
        """
        Получить список наград, предоставляемых этим источником.

        Returns:
            List[Reward]: Список объектов наград.
        """
        pass

# Конкретная реализация для монстра
class MonsterRewardSource(RewardSource):
    """
    Источник наград, связанный с конкретным типом монстра.
    Обычно создается на основе конфигурации монстра.
    """

    def __init__(self, monster_type: str, base_experience: int, level: int, items=None):
        """
        Инициализирует источник наград для монстра.

        Args:
            monster_type (str): Тип монстра (например, "goblin").
            base_experience (int): Базовое количество опыта за убийство.
            level (int): Уровень монстра (может влиять на награду).
            items (list, optional): Список возможных предметов. Defaults to None (заглушка).
        """
        self.monster_type = monster_type
        self.base_experience = base_experience
        self.level = level
        # self.items = items or [] # Заглушка для предметов

    def get_rewards(self) -> List['Reward']:
        """
        Получить список наград от монстра.
        Пока возвращает только награду опытом.
        """
        from game.rewards.types import ExperienceReward # Отложенное импортирование во избежание циклов
        rewards: List['Reward'] = []
        # Добавляем награду опытом
        if self.base_experience > 0:
             # Передаем уровень монстра в награду
            rewards.append(ExperienceReward(amount=self.base_experience, source_level=self.level))
        # TODO: Добавить ItemReward когда появится система предметов
        # for item_data in self.items:
        #     rewards.append(ItemReward(...))
        return rewards

# Фабрика для создания RewardSource из конфигурации монстра (опционально, но удобно)
# Можно поместить в тот же файл или в отдельный файл, например, sources_factory.py
# def create_reward_source_from_monster_config(config: MonsterConfig) -> RewardSource:
#     return MonsterRewardSource(
#         monster_type=config.role, # или отдельное поле в конфиге
#         base_experience=getattr(config, 'reward_exp', 0), # Получаем из конфига
#         level=config.level
#     )