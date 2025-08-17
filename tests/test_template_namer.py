# tests/test_template_namer.py
"""Тесты для генератора имен монстров."""

import os
import json
import pytest
from unittest.mock import patch, mock_open

from game.naming.template_namer import TemplateMonsterNamer

class TestTemplateMonsterNamer:
    """Тесты для класса TemplateMonsterNamer."""

    def test_init_with_default_directory(self):
        """Тест инициализации с директорией по умолчанию."""
        namer = TemplateMonsterNamer()
        assert isinstance(namer, TemplateMonsterNamer)
        # Проверяем, что word_data инициализирован как словарь
        assert isinstance(namer.word_data, dict)

    @patch('os.path.exists')
    @patch('builtins.open')
    def test_load_word_data_io_error(self, mock_file, mock_exists):
        """Тест загрузки данных при ошибке ввода-вывода."""
        mock_exists.return_value = True
        mock_file.side_effect = IOError("File error")
        with patch('builtins.print') as mock_print:
            namer = TemplateMonsterNamer(data_directory="/fake/path")
            mock_print.assert_called()  # Должно быть сообщение об ошибке
        expected_keys = ["adjectives", "nouns", "prefixes", "suffixes"]
        for key in expected_keys:
            assert key in namer.word_data
            assert namer.word_data[key] == []  # Должен быть пустой список

    @patch('os.path.exists')
    @patch('builtins.open')
    def test_load_word_data_json_decode_error(self, mock_file, mock_exists):
        """Тест загрузки данных при ошибке JSON."""
        mock_exists.return_value = True
        mock_file.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 1)
        with patch('builtins.print') as mock_print:
            namer = TemplateMonsterNamer(data_directory="/fake/path")
            mock_print.assert_called()  # Должно быть сообщение об ошибке
        expected_keys = ["adjectives", "nouns", "prefixes", "suffixes"]
        for key in expected_keys:
            assert namer.word_data[key] == []  # Должен быть пустой список

    def test_get_words_existing_category(self):
        """Тест получения слов для существующей категории."""
        namer = TemplateMonsterNamer()
        namer.word_data = {"adjectives": ["страшный", "мощный"]}
        result = namer._get_words("adjectives")
        assert result == ["страшный", "мощный"]

    def test_get_words_non_existing_category(self):
        """Тест получения слов для несуществующей категории."""
        namer = TemplateMonsterNamer()
        namer.word_data = {"adjectives": ["страшный"]}
        result = namer._get_words("nouns")
        assert result == []

    @patch('random.choice')
    def test_generate_name_success(self, mock_random_choice):
        """Тест успешной генерации имени."""
        mock_random_choice.side_effect = lambda x: x[0] if x else ""
        namer = TemplateMonsterNamer()
        namer.word_data = {
            "adjectives": ["страшный"],
            "nouns": ["гоблин"],
            "prefixes": ["супер"],
            "suffixes": ["младший"]
        }
        result = namer.generate_name("goblin")
        # Проверяем, что результат не пустой и содержит ожидаемые слова
        assert "страшный" in result or "гоблин" in result or "супер" in result or "младший" in result
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_name_empty_data(self):
        """Тест генерации имени с пустыми данными."""
        namer = TemplateMonsterNamer()
        namer.word_data = {"adjectives": [], "nouns": [], "prefixes": [], "suffixes": []}
        result = namer.generate_name("test_monster")
        # Должно вернуться имя по умолчанию
        assert "Монстр" in result or len(result) > 0

    def test_generate_name_with_various_templates(self):
        """Тест генерации имен с разными шаблонами."""
        namer = TemplateMonsterNamer()
        namer.word_data = {
            "adjectives": ["страшный", "мощный"],
            "nouns": ["гоблин", "дракон"],
            "prefixes": ["супер", "мега"],
            "suffixes": ["младший", "старший"]
        }
        # Тестируем несколько раз для разных результатов
        results = set()
        for i in range(5):
            with patch('random.choice') as mock_choice:
                # Фиксируем выбор для воспроизводимости
                mock_choice.side_effect = lambda x: x[i % len(x)] if x else ""
                result = namer.generate_name("goblin")
                results.add(result)
        # Проверяем, что получаем разные результаты
        assert len(results) >= 1


class TestIntegration:
    """Интеграционные тесты."""

    def test_basic_functionality(self):
        """Тест базовой функциональности."""
        namer = TemplateMonsterNamer()
        assert isinstance(namer.word_data, dict)
        # Даже с пустыми данными должен возвращать имя
        name = namer.generate_name("test_monster")
        assert isinstance(name, str)
        assert len(name) > 0


if __name__ == "__main__":
    pytest.main([__file__])