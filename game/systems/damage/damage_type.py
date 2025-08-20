"""
Модуль определения типов урона в игре.
Использует Enum для типобезопасности и автодополнения.
"""
from enum import Enum, auto


class DamageType(Enum):
    """
    Перечисление типов урона в игре.
    
    Каждый тип урона имеет уникальные свойства и взаимодействия,
    которые определяются в DamageTypeSystem.
    """
    PHYSICAL = auto()      # Обычный физический урон (мечи, стрелы)
    FIRE = auto()          # Огненный урон (заклинания огня)
    ICE = auto()           # Ледяной урон (заморозка, замедление)  
    LIGHTNING = auto()     # Электрический урон (молнии, шок)
    POISON = auto()        # Ядовитый урон (дот-урон, ослабление)
    HOLY = auto()          # Священный урон (против нежити, тьмы)
    DARK = auto()          # Темный урон (против света, живых)
    TRUE = auto()          # Чистый урон (игнорирует всю защиту)


# Опционально: алиасы для удобства
PHYSICAL = DamageType.PHYSICAL
FIRE = DamageType.FIRE
ICE = DamageType.ICE
LIGHTNING = DamageType.LIGHTNING
POISON = DamageType.POISON
HOLY = DamageType.HOLY
DARK = DamageType.DARK
TRUE = DamageType.TRUE