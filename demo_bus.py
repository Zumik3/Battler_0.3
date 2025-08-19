# demo_stats_health.py
"""Демонстрационный файл для создания и взаимодействия StatsProperty и HealthProperty."""

# Предполагаем, что ваши классы находятся в следующих модулях.
# Пути могут отличаться в вашем проекте.
from game.core.context import ContextFactory
from game.entities.properties import base
from game.entities.properties.combat import CombatProperty
from game.entities.properties.context import GameContextBasedPropertyContext
from game.entities.properties.energy import EnergyProperty
from game.entities.properties.experience import ExperienceProperty
from game.entities.properties.level import LevelProperty
from game.events.bus import EventBus
from game.entities.properties.stats import StatsProperty
from game.entities.properties.health import HealthProperty
from game.factories.player_factory import PlayerFactory

def main():
    """Основная функция для демонстрации."""
    print("--- Создание game_context ---")
    context = ContextFactory.create_default_context()
    
    player1 = PlayerFactory.create_player(context, "berserker")


    print("\n--- Демонстрация завершена ---")

if __name__ == "__main__":
    main()
