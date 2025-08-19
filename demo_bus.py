# demo_stats_health.py
"""Демонстрационный файл для создания и взаимодействия StatsProperty и HealthProperty."""

# Предполагаем, что ваши классы находятся в следующих модулях.
# Пути могут отличаться в вашем проекте.
from game.core.context import ContextFactory
from game.entities.properties import base
from game.entities.properties.context import GameContextBasedPropertyContext
from game.entities.properties.energy import EnergyProperty
from game.entities.properties.experience import ExperienceProperty
from game.entities.properties.level import LevelProperty
from game.events.bus import EventBus
from game.entities.properties.stats import StatsProperty
from game.entities.properties.health import HealthProperty

def main():
    """Основная функция для демонстрации."""
    print("--- Создание EventBus ---")
    # 1. Создаем шину событий
    game_context = ContextFactory.create_default_context()
    property_context = GameContextBasedPropertyContext(game_context)

    print(f"game_context создан: {game_context}\n")

    print("--- Создание StatsProperty ---")
    # 2. Создаем свойство характеристик
    # Передаем EventBus в конструктор
    stats = StatsProperty(property_context)
    print(f"StatsProperty создано: {stats}")
    print(f"  Начальные характеристики: str={stats.strength}, agi={stats.agility}, "
          f"int={stats.intelligence}, vit={stats.vitality}\n")

    print("--- Создание HealthProperty ---")
    # 3. Создаем свойство здоровья
    # Передаем ему stats и тот же EventBus
    # HealthProperty должно автоматически подписаться на события от stats
    health = HealthProperty(property_context, stats=stats)
    print(f"HealthProperty создано: {health}")
    print(f"  Начальное здоровье: {health.health}/{health.max_health}\n")

    energy = EnergyProperty(property_context, stats=stats)
    print(f"EnergyProperty создано: {energy}")
    print(f"  Начальная энергия: {energy.energy}/{energy.max_energy}\n")

    exp = ExperienceProperty(property_context)
    level = LevelProperty(property_context, exp_property=exp)
    
    exp.add_experience(50)

    print(f"После пакетного изменения:")
    print(f"  Stats: str={stats.strength}, agi={stats.agility}, "
          f"int={stats.intelligence}, vit={stats.vitality}")
    print(f"  Health: {health.health}/{health.max_health}")
    print(f"  Energy: {energy.energy}/{energy.max_energy}\n")
    # Ожидается: max_health = 100 + 20 * 10 = 300


    health.cleanup()
    energy.cleanup()

    level.cleanup()

    print("\n--- Демонстрация завершена ---")

if __name__ == "__main__":
    main()
