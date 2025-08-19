# demo_stats_health.py
"""Демонстрационный файл для создания и взаимодействия StatsProperty и HealthProperty."""

# Предполагаем, что ваши классы находятся в следующих модулях.
# Пути могут отличаться в вашем проекте.
from game.core.context import ContextFactory
from game.factories.player_factory import PlayerFactory
from game.factories.monster_factory import MonsterFactory

def main():
    """Основная функция для демонстрации."""
    print("--- Создание game_context ---")
    context = ContextFactory.create_default_context()
    
    player1 = PlayerFactory.create_player(context, "berserker")
    print("\nPlayer done")
    monster1 = MonsterFactory.create_monster(context, "goblin", 5)

    print("\n--- Демонстрация завершена ---")

if __name__ == "__main__":
    main()
