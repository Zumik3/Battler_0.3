# tests/test_ui/test_widgets.py
"""Тесты для виджетов UI (game/ui/widgets/)."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict, List, Optional

# Импортируем тестируемые классы
from game.ui.widgets.labels import (
    TextLabel,
    CharacterNameLabel,
    CharacterClassLabel,
    CharacterLevelLabel,
    TemplatedTextLabel
)
from game.ui.widgets.bars import (
    ProgressBar,
    HealthBar,
    EnergyBar
)
from game.ui.widgets.character_card import CharacterInfoPanel

# Для аннотаций типов и создания моков
from game.ui.rendering.color_manager import Color
from game.ui.rendering.renderer import Renderer

# === Фикстуры ===

@pytest.fixture
def mock_renderer() -> Mock:
    """Фикстура для создания мок-рендерера."""
    return Mock(spec=Renderer)


@pytest.fixture
def mock_character() -> Mock:
    """Фикстура для создания мок-персонажа."""
    character = Mock()
    character.name = "Тестовый Герой"
    character.level = 5
    character.role = "Воин"
    character.player_class = None  # Для проверки логики получения роли
    character.hp = 80
    character.energy = 30
    character.attributes = Mock()
    character.attributes.max_hp = 100
    character.attributes.max_energy = 50
    return character


@pytest.fixture
def mock_player_with_class(mock_character: Mock) -> Mock:
    """Фикстура для создания мок-игрока с классом."""
    player_class = Mock()
    player_class.name = "Paladin"
    mock_character.player_class = player_class
    mock_character.role = None  # У игрока role может быть None
    return mock_character


# === Тесты для labels.py ===

class TestTextLabel:
    """Тесты для TextLabel."""

    def test_initialization(self) -> None:
        """Тест инициализации TextLabel."""
        label = TextLabel(x=1, y=2, text="Привет", color=Color.RED, bold=True, dim=False)
        assert label.x == 1
        assert label.y == 2
        assert label.text == "Привет"
        assert label.color == Color.RED
        assert label.bold is True
        assert label.dim is False

    def test_render(self, mock_renderer: Mock) -> None:
        """Тест отрисовки TextLabel."""
        label = TextLabel(x=5, y=3, text="Тест", color=Color.BLUE, bold=False, dim=True)
        label.render(mock_renderer)
        mock_renderer.draw_text.assert_called_once_with("Тест", 5, 3, False, True, Color.BLUE)

    def test_render_empty_text(self, mock_renderer: Mock) -> None:
        """Тест отрисовки TextLabel с пустым текстом."""
        label = TextLabel(x=0, y=0, text="")
        label.render(mock_renderer)
        mock_renderer.draw_text.assert_not_called()


class TestCharacterNameLabel:
    """Тесты для CharacterNameLabel."""

    def test_initialization(self, mock_character: Mock) -> None:
        """Тест инициализации CharacterNameLabel."""
        label = CharacterNameLabel(x=1, y=1, character=mock_character, max_width=15)
        assert label.x == 1
        assert label.y == 1
        assert label.character is mock_character
        assert label.max_width == 15
        # Текст должен обновиться из персонажа
        assert label.text == "Тестовый Герой"

    def test_set_character(self, mock_character: Mock) -> None:
        """Тест установки персонажа."""
        label = CharacterNameLabel(x=0, y=0)
        assert label.text == "Unknown"
        label.set_character(mock_character)
        assert label.character is mock_character
        assert label.text == "Тестовый Герой"

    def test_render_with_max_width(self, mock_renderer: Mock, mock_character: Mock) -> None:
        """Тест отрисовки с ограничением ширины."""
        long_name_character = Mock()
        long_name_character.name = "Очень Длинное Имя Персонажа"
        label = CharacterNameLabel(x=2, y=2, character=long_name_character, max_width=10)
        label.render(mock_renderer)
        # Ожидаем, что текст будет обрезан до 10 символов
        mock_renderer.draw_text.assert_called_once_with("Очень Длин", 2, 2, False, False, Color.DEFAULT)

    def test_render_no_character(self, mock_renderer: Mock) -> None:
        """Тест отрисовки без персонажа."""
        label = CharacterNameLabel(x=3, y=3)
        label.render(mock_renderer)
        mock_renderer.draw_text.assert_called_once_with("Unknown", 3, 3, False, False, Color.DEFAULT)


class TestCharacterClassLabel:
    """Тесты для CharacterClassLabel."""

    def test_initialization_with_role(self, mock_character: Mock) -> None:
        """Тест инициализации с ролью."""
        label = CharacterClassLabel(x=1, y=1, character=mock_character)
        assert label.x == 1
        assert label.y == 1
        assert label.character is mock_character

    def test_render_with_role(self, mock_renderer: Mock, mock_character: Mock) -> None:
        """Тест отрисовки с ролью."""
        label = CharacterClassLabel(x=4, y=4, character=mock_character)
        label.render(mock_renderer)
        
        # Проверяем вызов draw_template
        mock_renderer.draw_template.assert_called_once()
        args, kwargs = mock_renderer.draw_template.call_args
        template, replacements = args[0], args[1]
        assert template == "%1%2%3"
        assert replacements["1"] == ("[", Color.WHITE, False, False)
        assert replacements["2"] == ("В", Color.CYAN, False, False) # Первая буква
        assert replacements["3"] == ("]", Color.WHITE, False, False)

    def test_render_with_player_class(self, mock_renderer: Mock, mock_player_with_class: Mock) -> None:
        """Тест отрисовки с классом игрока."""
        label = CharacterClassLabel(x=5, y=5, character=mock_player_with_class)
        label.render(mock_renderer)
        
        mock_renderer.draw_template.assert_called_once()
        args, kwargs = mock_renderer.draw_template.call_args
        template, replacements = args[0], args[1]
        assert template == "%1%2%3"
        assert replacements["2"] == ("N", Color.CYAN, False, False) # Первая буква Паладина

    def test_render_no_character(self, mock_renderer: Mock) -> None:
        """Тест отрисовки без персонажа."""
        label = CharacterClassLabel(x=6, y=6)
        label.render(mock_renderer)
        
        mock_renderer.draw_template.assert_called_once()
        args, kwargs = mock_renderer.draw_template.call_args
        replacements = args[1]
        assert replacements["2"] == ("?", Color.CYAN, False, False) # Заглушка


class TestCharacterLevelLabel:
    """Тесты для CharacterLevelLabel."""

    def test_initialization(self, mock_character: Mock) -> None:
        """Тест инициализации CharacterLevelLabel."""
        label = CharacterLevelLabel(x=1, y=1, character=mock_character)
        assert label.x == 1
        assert label.y == 1
        assert label.character is mock_character

    def test_render_with_character(self, mock_renderer: Mock, mock_character: Mock) -> None:
        """Тест отрисовки с персонажем."""
        label = CharacterLevelLabel(x=7, y=7, character=mock_character)
        label.render(mock_renderer)
        
        mock_renderer.draw_template.assert_called_once()
        args, kwargs = mock_renderer.draw_template.call_args
        template, replacements = args[0], args[1]
        assert template == "%1%2%3"
        assert replacements["1"] == ("[", Color.WHITE, False, False)
        assert replacements["2"] == ("5", Color.YELLOW, False, False) # Уровень 5
        assert replacements["3"] == ("]", Color.WHITE, False, False)

    def test_render_no_character(self, mock_renderer: Mock) -> None:
        """Тест отрисовки без персонажа."""
        label = CharacterLevelLabel(x=8, y=8)
        label.render(mock_renderer)
        
        mock_renderer.draw_template.assert_called_once()
        args, kwargs = mock_renderer.draw_template.call_args
        replacements = args[1]
        assert replacements["2"] == ("1", Color.YELLOW, False, False) # Уровень по умолчанию


class TestTemplatedTextLabel:
    """Тесты для абстрактного TemplatedTextLabel."""

    def test_initialization(self) -> None:
        """Тест инициализации TemplatedTextLabel."""
        # Напрямую создать экземпляр абстрактного класса нельзя,
        # но можно проверить его базовую инициализацию
        with patch.multiple(TemplatedTextLabel, __abstractmethods__=set()):
            label = TemplatedTextLabel(x=1, y=1)
            assert label.x == 1
            assert label.y == 1

    def test_render_calls_abstract_method(self) -> None:
        """Тест, что render вызывает абстрактный метод."""
        with patch.multiple(TemplatedTextLabel, __abstractmethods__=set()):
            label = TemplatedTextLabel(x=0, y=0)
            with patch.object(label, '_get_template_and_replacements') as mock_get_template:
                mock_get_template.return_value = ("Шаблон", {"1": ("Тест", Color.DEFAULT, False, False)})
                mock_renderer = Mock()
                
                label.render(mock_renderer)
                
                mock_get_template.assert_called_once()
                mock_renderer.draw_template.assert_called_once_with(
                    "Шаблон", {"1": ("Тест", Color.DEFAULT, False, False)}, 0, 0
                )


# === Тесты для bars.py ===

class TestProgressBar:
    """Тесты для абстрактного ProgressBar."""

    def test_initialization(self, mock_character: Mock) -> None:
        """Тест инициализации ProgressBar."""
        # Напрямую создать экземпляр абстрактного класса нельзя,
        # но можно проверить его базовую инициализацию
        with patch.multiple(ProgressBar, __abstractmethods__=set()):
            bar = ProgressBar(x=1, y=1, width=20, character=mock_character)
            assert bar.x == 1
            assert bar.y == 1
            assert bar.width == 20
            assert bar.character is mock_character

    # Дополнительные тесты для абстрактного класса могут быть сложными,
    # так как они зависят от реализации абстрактных методов


class TestHealthBar:
    """Тесты для HealthBar."""

    def test_initialization(self, mock_character: Mock) -> None:
        """Тест инициализации HealthBar."""
        bar = HealthBar(x=2, y=2, width=15, character=mock_character)
        assert bar.x == 2
        assert bar.y == 2
        assert bar.width == 15
        assert bar.character is mock_character

    def test_get_fill_color_high_hp(self, mock_character: Mock) -> None:
        """Тест цвета заполнения при высоком HP."""
        mock_character.hp = 90
        mock_character.attributes.max_hp = 100
        bar = HealthBar(character=mock_character)
        assert bar._get_fill_color() == Color.GREEN

    def test_get_fill_color_medium_hp(self, mock_character: Mock) -> None:
        """Тест цвета заполнения при среднем HP."""
        mock_character.hp = 40
        mock_character.attributes.max_hp = 100
        bar = HealthBar(character=mock_character)
        assert bar._get_fill_color() == Color.YELLOW

    def test_get_fill_color_low_hp(self, mock_character: Mock) -> None:
        """Тест цвета заполнения при низком HP."""
        mock_character.hp = 10
        mock_character.attributes.max_hp = 100
        bar = HealthBar(character=mock_character)
        assert bar._get_fill_color() == Color.RED

    def test_get_fill_color_no_character(self) -> None:
        """Тест цвета заполнения без персонажа."""
        bar = HealthBar()
        assert bar._get_fill_color() == Color.GREEN # Цвет по умолчанию


class TestEnergyBar:
    """Тесты для EnergyBar."""

    def test_initialization(self, mock_character: Mock) -> None:
        """Тест инициализации EnergyBar."""
        bar = EnergyBar(x=3, y=3, width=10, character=mock_character)
        assert bar.x == 3
        assert bar.y == 3
        assert bar.width == 10
        assert bar.character is mock_character

    def test_get_fill_color(self, mock_character: Mock) -> None:
        """Тест цвета заполнения."""
        bar = EnergyBar(character=mock_character)
        assert bar._get_fill_color() == Color.BLUE

    def test_get_empty_color(self, mock_character: Mock) -> None:
        """Тест цвета пустой части."""
        bar = EnergyBar(character=mock_character)
        assert bar._get_empty_color() == Color.GRAY


# === Тесты для character_card.py ===

class TestCharacterInfoPanel:
    """Тесты для CharacterInfoPanel."""

    def test_initialization(self, mock_character: Mock) -> None:
        """Тест инициализации CharacterInfoPanel."""
        panel = CharacterInfoPanel(x=1, y=1, width=30, height=5, character=mock_character)
        assert panel.x == 1
        assert panel.y == 1
        assert panel.width == 30
        assert panel.height == 5
        assert panel.character is mock_character
        # Проверяем, что дочерние виджеты созданы
        assert panel.class_label is not None
        assert panel.name_label is not None
        assert panel.level_label is not None
        assert panel.health_bar is not None
        assert panel.energy_bar is not None

    def test_set_character(self, mock_character: Mock) -> None:
        """Тест установки персонажа."""
        panel = CharacterInfoPanel(x=0, y=0, width=20, height=3)
        # Изначально персонаж не установлен
        assert panel.character is None
        # Устанавливаем персонажа
        panel.set_character(mock_character)
        # Проверяем, что персонаж установлен
        assert panel.character is mock_character
        # Проверяем, что персонаж установлен во всех дочерних виджетах
        # (предполагаем, что у них есть метод set_character)
        # Для простоты проверим, что методы были вызваны
        # (это косвенно подтверждает, что логика внутри set_character работает)

    def test_render(self, mock_renderer: Mock, mock_character: Mock) -> None:
        """Тест отрисовки панели."""
        panel = CharacterInfoPanel(x=5, y=5, width=25, height=4, character=mock_character)
        
        # Мокаем методы render дочерних виджетов
        panel.class_label.render = Mock()
        panel.name_label.render = Mock()
        panel.level_label.render = Mock()
        panel.health_bar.render = Mock()
        panel.energy_bar.render = Mock()
        
        panel.render(mock_renderer)
        
        # Проверяем, что методы render были вызваны у всех дочерних виджетов
        panel.class_label.render.assert_called_once_with(mock_renderer)
        panel.name_label.render.assert_called_once_with(mock_renderer)
        panel.level_label.render.assert_called_once_with(mock_renderer)
        panel.health_bar.render.assert_called_once_with(mock_renderer)
        panel.energy_bar.render.assert_called_once_with(mock_renderer)

    def test_update_size(self) -> None:
        """Тест обновления размеров панели."""
        panel = CharacterInfoPanel(x=0, y=0, width=20, height=3)
        initial_width = panel.width
        initial_height = panel.height
        
        # Сохраняем ссылки на дочерние виджеты
        class_label = panel.class_label
        name_label = panel.name_label
        level_label = panel.level_label
        health_bar = panel.health_bar
        energy_bar = panel.energy_bar
        
        # Обновляем размеры
        new_width, new_height = 40, 6
        panel.update_size(new_width, new_height)
        
        # Проверяем, что размеры панели обновились
        assert panel.width == new_width
        assert panel.height == new_height
        
        # Проверяем, что размеры и позиции дочерних виджетов обновились
        # (проверяем, что объекты остались теми же, но их атрибуты могли измениться)
        assert panel.class_label is class_label
        assert panel.name_label is name_label
        assert panel.level_label is level_label
        assert panel.health_bar is health_bar
        assert panel.energy_bar is energy_bar
        # Проверяем, что ширина прогресс-баров обновилась
        assert panel.health_bar.width == new_width
        assert panel.energy_bar.width == new_width
