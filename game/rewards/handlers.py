# game/rewards/handlers.py
"""Обработчики событий, связанных с наградами."""

from typing import TYPE_CHECKING

# Импортируем событие, на которое подписываемся
from game.events.battle_events import BattleEndedEvent 
# Импортируем тип результата боя, который будет в событии
from game.systems.battle.result import BattleResult

# Отложенные импорты для избежания циклических зависимостей
if TYPE_CHECKING:
    from game.core.context import GameContext
    # from game.rewards.calculator import RewardCalculator # Импортируем внутри функции

def handle_battle_ended_for_rewards(event: BattleEndedEvent) -> None:
    """
    Обработчик события окончания боя для запуска системы наград.
    
    Args:
        event (BattleEndedEvent): Событие окончания боя, содержащее BattleResult.
    """
    # Получаем BattleResult из события
    # Уточняем тип для mypy и лучшей читаемости
    battle_result: BattleResult = event.result
    
    # Проверка на случай, если вдруг результат не того типа (защитное программирование)
    if not isinstance(battle_result, BattleResult):
        # Можно залогировать ошибку
        print(f"Ошибка: Ожидался BattleResult, получен {type(battle_result)}")
        return
        
    # Проверяем, есть ли выжившие игроки
    if not battle_result.alive_players:
        # Нет выживших, наград не будет
        # print("Нет выживших игроков, награды не выдаются.") # Для отладки
        return
        
    # Получаем контекст из первого выжившего игрока
    # Это предполагает, что все игроки используют один и тот же контекст
    context = battle_result.alive_players[0].context
    
    # Создаем калькулятор наград
    from game.systems.rewards.calculator import RewardCalculator # Отложенный импорт
    calculator = RewardCalculator(context)
    
    # Запускаем расчет и распределение наград
    calculator.calculate_and_distribute(battle_result)

# Функция для регистрации обработчика (вызывается при инициализации игры)
def register_reward_handlers(context: 'GameContext') -> None:
    """
    Регистрирует обработчики событий наград в шине событий.
    
    Args:
        context (GameContext): Игровой контекст, содержащий EventBus.
    """
    # Подписываемся на BattleEndedEvent. 
    # Источник=None означает, что мы слушаем это событие от любого источника.
    # Приоритет 0 (HIGH_PRIORITY из event_bus.py), чтобы награды выдавались 
    # до других пост-боевых действий, если они тоже слушают это событие.
    context.event_bus.subscribe(
        source=None, # Слушаем от всех
        event_type=BattleEndedEvent,
        callback=handle_battle_ended_for_rewards,
        priority=0 # HIGH_PRIORITY
    )

# Если в будущем появятся другие обработчики наград, их можно добавить сюда
# и зарегистрировать в register_reward_handlers
