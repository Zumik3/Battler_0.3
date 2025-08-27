# game/ai/factory.py
"""Фабрика для создания экземпляров ИИ по имени типа."""

from typing import TYPE_CHECKING, Dict, Type, Optional, Any

from game.ai.decision_makers.basic_enemy_ai import BasicEnemyAI
from game.ai.decision_makers.healer_ai import HealerAI
from game.ai.decision_makers.player_ai import PlayerAI
# ... импортируем другие типы ИИ по мере их создания ...

if TYPE_CHECKING:
    from game.ai.ai_decision_maker import AIDecisionMaker

# --- Маппинг имя_типа -> класс ---
# Этот словарь сопоставляет строковое имя типа ИИ из конфигурационного файла
# с соответствующим классом Python.
_AI_TYPES: Dict[str, Type['AIDecisionMaker']] = {
    "BasicEnemyAI": BasicEnemyAI,
    "HealerAI": HealerAI,
    "PlayerAI": PlayerAI,
    # ... другие сопоставления ...
}
# --- Конец маппинга ---


def create_ai(ai_config: Optional[Dict[str, Any]]) -> Optional['AIDecisionMaker']:
    """
    Создает экземпляр ИИ на основе конфигурации.

    Эта функция является точкой входа для создания любого ИИ для персонажа.
    Она анализирует словарь конфигурации, извлекает имя типа ИИ,
    находит соответствующий класс в внутреннем реестре и создает его экземпляр.

    Args:
        ai_config: Словарь с конфигурацией ИИ из JSON.
                   Ожидается формат:
                   {
                       "type": "ИмяКлассаИИ",  # Обязательное поле
                       "params": {...}         # Опциональные параметры для конструктора (если будут)
                   }
                   Если None или пустой словарь, функция возвращает None.

    Returns:
        Экземпляр подкласса AIDecisionMaker или None, если:
        - ai_config был None или не содержал ключ 'type'.
        - Тип ИИ, указанный в 'type', не найден в реестре _AI_TYPES.
        - Произошла ошибка при создании экземпляра ИИ.

    Пример:
        >>> config = {"type": "BasicEnemyAI"}
        >>> ai_instance = create_ai(config)
        >>> print(type(ai_instance).__name__)
        BasicEnemyAI

        >>> config_unknown = {"type": "NonExistentAI"}
        >>> ai_instance = create_ai(config_unknown)
        >>> print(ai_instance)
        None
    """
    # 1. Проверка на наличие конфигурации
    if not ai_config:
        return None

    # 2. Извлечение имени типа ИИ из конфигурации
    ai_type_name = ai_config.get("type")
    
    # 3. Проверка, указан ли тип
    if not ai_type_name:
        print("Предупреждение: В конфигурации ИИ отсутствует поле 'type'.")
        return None

    # 4. Поиск класса ИИ в реестре
    ai_class = _AI_TYPES.get(ai_type_name)
    
    # 5. Проверка, найден ли класс
    if not ai_class:
        print(f"Ошибка: Неизвестный тип ИИ '{ai_type_name}'.")
        return None

    # 6. Извлечение параметров для конструктора (если предусмотрено)
    # params = ai_config.get("params", {}) # Раскомментировать, когда понадобятся параметры

    # 7. Создание экземпляра ИИ
    try:
        # Если будут параметры, передавать их в конструктор:
        # return ai_class(**params)
        # Пока создаем без параметров
        return ai_class()
    except Exception as e:
        print(f"Ошибка при создании ИИ типа '{ai_type_name}': {e}")
        return None
