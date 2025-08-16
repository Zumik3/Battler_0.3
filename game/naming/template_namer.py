# game/naming/template_namer.py
"""Генератор имен монстров на основе шаблонов."""

import random
import json
import os
from typing import List, Dict
from game.protocols import MonsterNamerProtocol

class TemplateMonsterNamer(MonsterNamerProtocol):
    """Простой генератор имен монстров, использующий шаблоны и списки слов."""

    def __init__(self, data_directory: str = "game/data/names"):
        """
        Инициализирует генератор.

        Args:
            data_directory: Путь к директории с JSON-файлами слов.
        """
        self.data_directory = data_directory
        self.word_data: Dict[str, List[str]] = {}
        self._load_word_data()

    def _load_word_data(self) -> None:
        """Загружает данные слов из JSON-файлов."""
        self.word_data = {}
        if not os.path.exists(self.data_directory):
            print(f"Предупреждение: Директория данных имен '{self.data_directory}' не найдена.")
            return

        try:
            # Загружаем общие списки слов
            common_files = {
                "adjectives": "adjectives.json",
                "nouns": "nouns.json",
                "prefixes": "prefixes.json",
                "suffixes": "suffixes.json",
            }
            for key, filename in common_files.items():
                filepath = os.path.join(self.data_directory, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.word_data[key] = json.load(f)
                else:
                    print(f"Предупреждение: Файл данных имен '{filepath}' не найден.")
                    self.word_data[key] = [] # Пустой список по умолчанию

            # Можно добавить загрузку специфичных для роли списков позже
            # Например, monster_role_adjectives.json

        except json.JSONDecodeError as e:
            print(f"Ошибка: Некорректный JSON в файлах имен: {e}")
            self.word_data = {k: [] for k in ["adjectives", "nouns", "prefixes", "suffixes"]}
        except Exception as e:
            print(f"Ошибка при загрузке данных имен: {e}")
            self.word_data = {k: [] for k in ["adjectives", "nouns", "prefixes", "suffixes"]}

    def _get_words(self, category: str) -> List[str]:
        """Получает список слов по категории. Возвращает пустой список, если категория отсутствует."""
        return self.word_data.get(category, [])

    def generate_name(self, monster_role: str) -> str:
        """
        Генерирует имя для монстра на основе его роли.

        Args:
            monster_role: Роль/тип монстра (например, 'goblin', 'dragon').

        Returns:
            Сгенерированное имя.
        """
        # Простые шаблоны
        templates = [
            "{adjective} {noun}",
            "{prefix}{noun}",
            "{noun} {suffix}",
            "{adjective} {prefix}{noun}",
            "{prefix}{noun} {suffix}",
            "{noun}", # Резервный вариант
        ]

        # Можно сделать шаблоны зависимыми от роли в будущем
        # role_templates = self._load_role_templates(monster_role)
        # if role_templates:
        #     templates = role_templates

        template = random.choice(templates)

        # Получаем слова
        adjectives = self._get_words("adjectives")
        nouns = self._get_words("nouns")
        prefixes = self._get_words("prefixes")
        suffixes = self._get_words("suffixes")

        # Словарь для подстановки в шаблон
        replacements = {
            "adjective": random.choice(adjectives) if adjectives else "",
            "noun": random.choice(nouns) if nouns else "Монстр",
            "prefix": random.choice(prefixes) if prefixes else "",
            "suffix": random.choice(suffixes) if suffixes else "",
        }

        # Форматируем имя
        try:
            name = template.format(**replacements).strip()
            # Убираем лишние пробелы, которые могли остаться
            name = " ".join(name.split())
            if not name:
                name = f"{monster_role.capitalize()} {random.randint(1, 1000)}"
            return name
        except KeyError as e:
            # На случай, если в шаблоне будет неизвестный ключ
            print(f"Ошибка форматирования имени: неизвестный ключ {e} в шаблоне '{template}'. Используется резервное имя.")
            return f"{monster_role.capitalize()} {random.randint(1, 1000)}"
        except Exception as e:
            print(f"Неожиданная ошибка при генерации имени: {e}. Используется резервное имя.")
            return f"{monster_role.capitalize()} {random.randint(1, 1000)}"

# --- Глобальный экземпляр для удобства ---
_DEFAULT_NAMER: TemplateMonsterNamer = None # type: ignore

def get_default_namer() -> TemplateMonsterNamer:
    """Получить глобальный экземпляр генератора имен."""
    global _DEFAULT_NAMER
    if _DEFAULT_NAMER is None:
        _DEFAULT_NAMER = TemplateMonsterNamer()
    return _DEFAULT_NAMER

def generate_monster_name(monster_role: str) -> str:
    """
    Удобная функция для генерации имени монстра с использованием
    глобального экземпляра генератора.

    Args:
        monster_role: Роль/тип монстра.

    Returns:
        Сгенерированное имя.
    """
    return get_default_namer().generate_name(monster_role)
