# demo_stats_health.py
"""Демонстрационный файл для создания и взаимодействия StatsProperty и HealthProperty."""

# Предполагаем, что ваши классы находятся в следующих модулях.
# Пути могут отличаться в вашем проекте.
from game.actions.basic_attack import BasicAttack
from game.core.context import ContextFactory
from game.factories.player_factory import PlayerFactory
from game.factories.monster_factory import MonsterFactory
from game.ui.components.battle_components import BattleLog
from game.ui.controllers.battle_log_controller import BattleLogController

def main():
    """Основная функция для демонстрации."""
    print("--- Создание game_context ---")
    context = ContextFactory.create_default_context()
    
    player1 = PlayerFactory.create_player(context, "berserker")
    print("\nPlayer done")
    monster1 = MonsterFactory.create_monster(context, "goblin", 5)

    battle_log = BattleLog(1, 1, 100, 100)
    battle_controller = BattleLogController(context=context, battle_log=battle_log)
    battle_controller.activate()

    attack = BasicAttack(player1)
    attack.target = monster1
    attack.execute()

    battle_log.render()
    battle_controller.deactivate()

    print("\n--- Демонстрация завершена ---")

if __name__ == "__main__":
    main()
