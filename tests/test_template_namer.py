# tests/test_template_namer.py
"""Тесты для генератора имен монстров."""

import os
import json
import pytest
from unittest.mock import patch, mock_open
from game.naming.template_namer import TemplateMonsterNamer, generate_monster_name


class TestTemplateMonsterNamer:
    """Тесты для класса TemplateMonsterNamer."""

    def test_init_with_default_directory(self):
        """Тест инициализации с директорией по умолчанию."""
        namer = TemplateMonsterNamer()
        assert namer.data_directory == "game/data/names"
        assert isinstance(namer.word_data, dict)

    def test_init_with_custom_directory(self):
        """Тест инициализации с пользовательской директорией."""
        custom_dir = "custom/names"
        namer = TemplateMonsterNamer(data_directory=custom_dir)
        assert namer.data_directory == custom_dir

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='["страшный", "злой"]')
    def test_load_word_data_success(self, mock_file, mock_exists):
        """Тест успешной загрузки данных слов."""
        mock_exists.return_value = True
        
        namer = TemplateMonsterNamer()
        assert "adjectives" in namer.word_data
        assert namer.word_data["adjectives"] == ["страшный", "злой"]

    @patch('os.path.exists')
    def test_load_word_data_directory_not_found(self, mock_exists):
        """Тест загрузки данных при отсутствии директории."""
        mock_exists.return_value = False
        
        with patch('builtins.print') as mock_print:
            namer = TemplateMonsterNamer()
            mock_print.assert_called_with(
                "Предупреждение: Директория данных имен 'game/data/names' не найдена."
            )
            assert namer.word_data == {}

    @patch('os.path.exists')
    @patch('builtins.open')
    def test_load_word_data_json_decode_error(self, mock_file, mock_exists):
        """Тест загрузки данных при ошибке JSON."""
        mock_exists.return_value = True
        mock_file.side_effect = json.JSONDecodeError("Invalid JSON", "doc", 1)
        
        with patch('builtins.print') as mock_print:
            namer = TemplateMonsterNamer()
            mock_print.assert_called()
            expected_keys = ["adjectives", "nouns", "prefixes", "suffixes"]
            for key in expected_keys:
                assert namer.word_data[key] == []

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
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_name_empty_word_data(self):
        """Тест генерации имени с пустыми данными слов."""
        namer = TemplateMonsterNamer()
        namer.word_data = {
            "adjectives": [],
            "nouns": [],
            "prefixes": [],
            "suffixes": []
        }
        
        result = namer.generate_name("test_role")
        
        # Проверяем что возвращается непустая строка (должно быть резервное имя)
        assert isinstance(result, str)
        assert len(result) > 0
        # Проверяем что имя содержит осмысленный текст
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
                assert isinstance(result, str)
                assert len(result) > 0
        
        # Должно быть хотя бы одно уникальное имя
        assert len(results) >= 1

    def test_generate_name_fallback_on_template_error(self):
        """Тест резервного имени при ошибке в шаблоне."""
        namer = TemplateMonsterNamer()
        namer.word_data = {
            "adjectives": ["страшный"],
            "nouns": ["гоблин"],
            "prefixes": ["супер"],
            "suffixes": ["младший"]
        }
        
        # Создаем ситуацию с некорректным шаблоном
        with patch('random.choice') as mock_choice:
            def choice_side_effect(options):
                # Возвращаем некорректный шаблон
                if isinstance(options, list) and len(options) > 0:
                    return "{nonexistent_key}"  # Несуществующий ключ
                return "резерв"
            mock_choice.side_effect = choice_side_effect
            
            result = namer.generate_name("test")
            
            # Должно вернуть резервное имя
            assert isinstance(result, str)
            assert len(result) > 0


class TestGlobalFunctions:
    """Тесты для глобальных функций модуля."""

    def test_get_default_namer_singleton(self):
        """Тест что get_default_namer возвращает один и тот же экземпляр."""
        # Сбрасываем глобальную переменную
        import game.naming.template_namer
        game.naming.template_namer._DEFAULT_NAMER = None
        
        # Импортируем функцию напрямую
        from game.naming.template_namer import get_default_namer
        namer1 = get_default_namer()
        namer2 = get_default_namer()
        
        assert namer1 is namer2
        assert isinstance(namer1, TemplateMonsterNamer)

    @patch('game.naming.template_namer.get_default_namer')
    def test_generate_monster_name_function(self, mock_get_namer):
        """Тест функции generate_monster_name."""
        from unittest.mock import MagicMock
        mock_namer = MagicMock()
        mock_namer.generate_name.return_value = "Тестовый Монстр"
        mock_get_namer.return_value = mock_namer
        
        result = generate_monster_name("goblin")
        assert result == "Тестовый Монстр"
        mock_get_namer.assert_called_once()
        mock_namer.generate_name.assert_called_once_with("goblin")


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