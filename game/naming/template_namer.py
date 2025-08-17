# game/naming/template_namer.py
"""Генератор имен монстров на основе шаблонов."""

import random
import json
import os
from typing import List, Dict, Optional
from game.protocols import MonsterNamerProtocol

class TemplateMonsterNamer(MonsterNamerProtocol):
    """Простой генератор имен монстров, использующий шаблоны и списки слов."""

    def __init__(self, data_directory: Optional[str] = None):
        """
        Инициализирует генератор.

        Args:
            data_directory: Путь к директории с JSON-файлами слов.
        """
        if data_directory is None:
            from game.config import get_config
            data_directory = get_config().system.character_names_directory
            
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
                    self.word_data[key] = []
                    
        except (json.JSONDecodeError, Exception) as e:
            print(f"Ошибка при загрузке данных имен: {e}")
            self.word_data = {k: [] for k in common_files.keys()}

    def _get_words(self, category: str) -> List[str]:
        """Получает список слов по категории."""
        return self.word_data.get(category, [])

    def generate_name(self, monster_role: str) -> str:
        """
        Генерирует имя для монстра на основе его роли.
        """
        if not monster_role or not monster_role.strip():
            monster_role = "monster"

        templates = [
            "{adjective} {noun}",
            "{prefix}{noun}",
            "{noun} {suffix}",
            "{adjective} {prefix}{noun}",
            "{prefix}{noun} {suffix}",
            "{noun}",
        ]

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

        try:
            name = template.format(**replacements).strip()
            name = " ".join(name.split())
            return name if name else f"{monster_role.capitalize()} {random.randint(1, 1000)}"
        except (KeyError, Exception):
            return f"{monster_role.capitalize()} {random.randint(1, 1000)}"

# --- Фабрика для удобства ---
def create_default_namer() -> TemplateMonsterNamer:
    """Создать экземпляр генератора имен с настройками по умолчанию."""
    return TemplateMonsterNamer()

def generate_monster_name(monster_role: str) -> str:
    """
    Удобная функция для генерации имени монстра.
    """
    namer = create_default_namer()
    return namer.generate_name(monster_role)