# game/systems/rewards/calculator.py
"""Калькулятор и распределитель наград."""

import math
import random
from typing import List, TYPE_CHECKING

# Предполагаем, что BattleResult уже создан
from game.systems.battle.result import BattleResult

# Импортируем необходимые классы наград
from game.rewards.reward import Reward
from game.rewards.types import ExperienceReward # Импортируем конкретный тип

# Для создания источников наград напрямую (временно)
# В будущем это должно приходить из монстра или его конфигурации
from game.rewards.sources import MonsterRewardSource

# --- НОВЫЕ ИМПОРТЫ ДЛЯ РЕНДЕРИНГА ---
# Импортируем события и данные для рендеринга
from game.events.reward_events import PartyExperienceGainedEvent
from game.events.render_data import RenderData
from game.ui.rendering.color_manager import Color
# --- КОНЕЦ НОВЫХ ИМПОРТОВ ---

if TYPE_CHECKING:
    from game.entities.character import Character
    from game.core.game_context import GameContext # Для доступа к event_bus

class RewardCalculator:
    """
    Сервис для расчета и распределения наград после боя.
    """

    def __init__(self, context: 'GameContext'):
        """
        Инициализирует калькулятор наград.

        Args:
            context (GameContext): Игровой контекст для доступа к event_bus и другим сервисам.
        """
        self.context = context

    def calculate_and_distribute(self, battle_result: BattleResult) -> None:
        """
        Рассчитывает и распределает награды на основе результата боя.

        Args:
            battle_result (BattleResult): Результат завершенного боя.
        """
        if not battle_result.alive_players:
            # Никто не выжил, наград нет
            # В реальной системе это можно логировать
            # print("Нет выживших игроков, награды не выдаются.")
            return

        # 1. Собрать все награды от побежденных врагов
        all_rewards: List[Reward] = []
        for enemy in battle_result.dead_enemies:
            # ВРЕМЕННОЕ РЕШЕНИЕ: создаем источник на лету из данных монстра
            # Это потребует, чтобы у Monster были атрибуты reward_exp и т.д.
            # В будущем enemy может иметь атрибут enemy.reward_source: RewardSource
            
            # Получаем базовый опыт. Если атрибута нет, используем значение по умолчанию.
            base_exp = getattr(enemy, 'reward_exp', 10)
            
            # Получаем уровень. Упрощенная логика.
            enemy_level = 1
            if hasattr(enemy, 'level') and enemy.level:
                enemy_level = enemy.level.get_level()
            
            enemy_reward_source = MonsterRewardSource(
                monster_type=enemy.role,
                base_experience=base_exp,
                level=enemy_level
            )
            # Получаем награды от источника и добавляем их в общий список
            all_rewards.extend(enemy_reward_source.get_rewards())

        # 2. Обработать награды
        # Разделяем награды по типам для специальной обработки
        experience_rewards = [r for r in all_rewards if isinstance(r, ExperienceReward)]
        # item_rewards = [r for r in all_rewards if isinstance(r, ItemReward)] # Заглушка

        # 3. Распределить опыт
        self._distribute_experience(experience_rewards, battle_result.alive_players)

        # 4. Распределить предметы (заглушка)
        # self._distribute_items(item_rewards, battle_result.alive_players)

    def _distribute_experience(self, exp_rewards: List[ExperienceReward], recipients: List['Character']) -> None:
        """
        Суммирует весь опыт и распределяет его между выжившими игроками.

        Args:
            exp_rewards (List[ExperienceReward]): Список наград опытом.
            recipients (List[Character]): Список персонажей, получающих опыт.
        """
        if not recipients or not exp_rewards:
            return

        # 1. Суммируем весь опыт
        total_exp = sum(reward.amount for reward in exp_rewards)
        if total_exp <= 0:
            return

        # 2. Распределяем опыт между игроками
        self._distribute_total_experience(total_exp, recipients)

    def _distribute_total_experience(self, total_exp: int, recipients: List['Character']) -> None:
        """
        Распределяет суммарный опыт между выжившими игроками с небольшим разбросом
        и публикует агрегированное событие награды.

        Args:
            total_exp (int): Общее количество опыта для распределения.
            recipients (List[Character]): Список персонажей, получающих опыт.
        """
        # --- НОВОЕ: Словарь для сбора информации о распределении ---
        distribution_info: dict['Character', int] = {}
        # --- ---
        
        if len(recipients) == 0:
            return

        # Базовое количество опыта на игрока
        base_exp_per_player = total_exp // len(recipients)
        # Остаток опыта, который нужно распределить
        remainder_exp = total_exp % len(recipients)

        # Создаем список для хранения финального опыта каждого игрока
        final_exp_distribution = [base_exp_per_player] * len(recipients)

        # Распределяем остаток: добавляем 1 очко оставшимся игрокам
        for i in range(remainder_exp):
            final_exp_distribution[i] += 1

        # Применяем небольшой случайный разброс (±10%)
        # Для этого перераспределяем небольшую часть опыта
        total_to_redistribute = 0
        redistribution_indices = []
        
        for i in range(len(recipients)):
            # Определяем 10% от базового опыта игрока (минимум 1)
            ten_percent = max(1, int(final_exp_distribution[i] * 0.1))
            if ten_percent > 0 and final_exp_distribution[i] > ten_percent:
                # Выбираем случайное количество для перераспределения (до 10%)
                redistribute_amount = random.randint(0, ten_percent)
                if redistribute_amount > 0:
                    final_exp_distribution[i] -= redistribute_amount
                    total_to_redistribute += redistribute_amount
                    redistribution_indices.append(i)

        # Распределяем "украденный" опыт случайным образом между всеми игроками
        if total_to_redistribute > 0 and redistribution_indices:
            for _ in range(total_to_redistribute):
                # Выбираем случайного игрока для получения дополнительного опыта
                recipient_index = random.randint(0, len(recipients) - 1)
                final_exp_distribution[recipient_index] += 1

        # 3. Создаем и применяем награды для каждого игрока
        # --- ИЗМЕНЕНИЕ: Собираем информацию и применяем награду ---
        for i, player in enumerate(recipients):
            exp_amount = final_exp_distribution[i]
            if exp_amount > 0:
                # Собираем информацию для агрегированного события
                distribution_info[player] = exp_amount
                
                # Применяем награду (по-прежнему публикуется RewardExperienceGainedEvent)
                # Это нужно для индивидуальной обработки опыта каждым персонажем
                source_level = None # TODO: Определить, откуда брать source_level
                reward = ExperienceReward(amount=exp_amount, source_level=source_level)
                reward.apply(player) # Это публикует RewardExperienceGainedEvent
                # print(f"Применена награда: {reward} к {player.name}") # Для отладки
        # --- КОНЕЦ ИЗМЕНЕНИЯ ---

        # --- НОВОЕ: Создание и публикация агрегированного события ---
        if distribution_info and self.context: # Убедимся, что есть что публиковать и есть контекст
             # 1. Создаем RenderData с помощью нового метода
             render_data = self._create_party_exp_render_data(total_exp, distribution_info)

             # 2. Преобразуем словарь в список кортежей для события
             recipients_and_amounts_list = list(distribution_info.items())
            
             # 3. Создаем и публикуем событие
             party_event = PartyExperienceGainedEvent(
                 source=None,
                 recipients_and_amounts=recipients_and_amounts_list,
                 total_experience=total_exp,
                 render_data=render_data
             )
             self.context.event_bus.publish(party_event)
        # --- КОНЕЦ НОВОГО ---

    # --- НОВЫЙ МЕТОД ---
    def _create_party_exp_render_data(self, total_exp: int, distribution_info: dict['Character', int]) -> 'RenderData':
        """
        Создает RenderData для события PartyExperienceGainedEvent.

        Args:
            total_exp (int): Общее количество опыта.
            distribution_info (dict[Character, int]): Словарь {персонаж: количество опыта}.

        Returns:
            RenderData: Объект с шаблоном и заменами для рендеринга сообщения.
        """
        # Формируем строку с деталями: "Роланд: 5, Стайлс: 7"
        details_parts = []
        replacements = {}
        
        # Добавляем общее количество опыта как первую замену
        replacements["1"] = (f"{total_exp}", Color.YELLOW, True, False) # Желтый, жирный
        
        # Добавляем детали для каждого персонажа
        char_index = 2 # Начинаем с 2, так как 1 занято общим опытом
        exp_index = 3
        
        for char, exp in distribution_info.items():
            char_placeholder = str(char_index)
            exp_placeholder = str(exp_index)
            
            details_parts.append(f"%{char_placeholder}: %{exp_placeholder}")
            
            # Замена для имени персонажа (зеленый)
            replacements[char_placeholder] = (char.name, Color.GREEN, False, False)
            # Замена для количества опыта (желтый, жирный)
            replacements[exp_placeholder] = (f"{exp}", Color.YELLOW, True, False)
            
            char_index += 2 # Переходим к следующему персонажу
            exp_index += 2 # Переходим к следующему опыту

        details_string = ", ".join(details_parts)
        
        # Шаблон: "Группа получила %1 опыта (%2: %3, %4: %5)"
        template = f"Группа получила %1 опыта ({details_string})"
        
        return RenderData(template=template, replacements=replacements)
    # --- КОНЕЦ НОВОГО МЕТОДА ---

    # def _distribute_items(self, item_rewards: List['ItemReward'], recipients: List['Character']) -> None:
    #     """Распределяет предметы (заглушка)."""
    #     # TODO: Реализовать логику распределения предметов
    #     # Можно случайно, можно первому, можно в общий фонд
    #     pass