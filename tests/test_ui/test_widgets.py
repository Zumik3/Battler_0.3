# tests/test_ui/test_widgets.py
"""Тесты для UI виджетов."""

from typing import Any, Dict, List
from unittest.mock import Mock, patch, MagicMock

import pytest

from game.ui.rendering.renderer import Renderer
from game.ui.widgets.labels import (
    TextLabel, CharacterNameLabel, CharacterClassLabel, CharacterLevelLabel
)
from game.ui.widgets.bars import ProgressBar, HealthBar, EnergyBar
from game.ui.widgets.character_card import CharacterInfoPanel


# ==================== Фикстуры ====================

@pytest.fixture
def mock_renderer() -> Mock:
    """Фикстура для создания мок-рендерера."""
    return Mock(spec=Renderer)


@pytest.fixture
def mock_character() -> Mock:
    """Фикстура для создания мок-персонажа."""
    character = Mock()
    character.name = "Test Character"
    character.role = "warrior"
    character.level = 5
    character.class_icon = "W"
    character.class_icon_color = "CYAN"  # Используем строковое значение цвета
    return character


@pytest.fixture
def mock_player_with_class() -> Mock:
    """Фикстура для создания мок-игрока с классом."""
    player = Mock()
    player.name = "Test Player"
    player.role = "player"
    player.level = 3
    player.class_name = "Warrior"
    player.class_icon = "P"
    player.class_icon_color = "BLUE"  # Используем строковое значение цвета
    return player


# ==================== Тесты TextLabel ====================

class TestTextLabel:
    """Тесты для TextLabel."""

    def test_initialization(self, mock_renderer: Mock) -> None:
        """Тест инициализации TextLabel."""
        label = TextLabel(x=1, y=2, text="Test")
        assert label.x == 1
        assert label.y == 2
        assert label.text == "Test"

    def test_render(self, mock_renderer: Mock) -> None:
        """Тест отрисовки TextLabel."""
        label = TextLabel(x=3, y=4, text="Render Test")
        label.render(mock_renderer)
        mock_renderer.draw_text.assert_called_once_with("Render Test", 3, 4)


# ==================== Тесты CharacterNameLabel ====================

class TestCharacterNameLabel:
    """Тесты для CharacterNameLabel."""

    def test_initialization(self, mock_character: Mock) -> None:
        """Тест инициализации CharacterNameLabel."""
        label = CharacterNameLabel(x=0, y=0, character=mock_character)
        assert label.x == 0
        assert label.y == 0
        assert label.character == mock_character
        assert label.text == "Test Character"

    def test_set_character(self, mock_character: Mock) -> None:
        """Тест установки персонажа."""
        label = CharacterNameLabel(x=0, y=0, character=mock_character)
        # Создаем нового мок-персонажа
        new_character = Mock()
        new_character.name = "New Character"
        label.character = new_character
        assert label.character == new_character
        assert label.text == "New Character"

    def test_render_with_character(self, mock_renderer: Mock, mock_character: Mock) -> None:
        """Тест отрисовки с персонажем."""
        label = CharacterNameLabel(x=1, y=1, character=mock_character)
        label.render(mock_renderer)
        mock_renderer.draw_text.assert_called_once_with("Test Character", 1, 1)

    def test_render_no_character(self, mock_renderer: Mock) -> None:
        """Тест отрисовки без персонажа."""
        # Создаем мок-персонажа как None
        label = CharacterNameLabel(x=3, y=3, character=None)
        label.render(mock_renderer)
        mock_renderer.draw_text.assert_called_once_with("Unknown", 3, 3)


# ==================== Тесты CharacterClassLabel ====================

class TestCharacterClassLabel:
    """Тесты для CharacterClassLabel."""

    def test_initialization_with_role(self, mock_character: Mock) -> None:
        """Тест инициализации с ролью."""
        label = CharacterClassLabel(x=1, y=1, character=mock_character)
        assert label.x == 1
        assert label.y == 1
        assert label.character == mock_character
        assert label.text == "[W]"

    def test_render_with_role(self, mock_renderer: Mock, mock_character: Mock) -> None:
        """Тест отрисовки с ролью."""
        label = CharacterClassLabel(x=4, y=4, character=mock_character)
        label.render(mock_renderer)
        # Проверяем, что draw_text был вызван с правильными аргументами
        # Мы не можем точно проверить цвет, так как он преобразуется в enum
        mock_renderer.draw_text.assert_called_once()
        args, kwargs = mock_renderer.draw_text.call_args
        assert args[0] == "[W]"  # text
        assert args[1] == 4      # x
        assert args[2] == 4      # y

    def test_render_with_player_class(self, mock_renderer: Mock, mock_player_with_class: Mock) -> None:
        """Тест отрисовки с классом игрока."""
        label = CharacterClassLabel(x=5, y=5, character=mock_player_with_class)
        label.render(mock_renderer)
        mock_renderer.draw_text.assert_called_once()
        args, kwargs = mock_renderer.draw_text.call_args
        assert args[0] == "[P]"  # text
        assert args[1] == 5      # x
        assert args[2] == 5      # y

    def test_render_no_character(self, mock_renderer: Mock) -> None:
        """Тест отрисовки без персонажа."""
        label = CharacterClassLabel(x=6, y=6, character=None)
        label.render(mock_renderer)
        mock_renderer.draw_text.assert_called_once_with("[?]", 6, 6)


# ==================== Тесты CharacterLevelLabel ====================

class TestCharacterLevelLabel:
    """Тесты для CharacterLevelLabel."""

    def test_initialization(self, mock_character: Mock) -> None:
        """Тест инициализации CharacterLevelLabel."""
        label = CharacterLevelLabel(x=2, y=2, character=mock_character)
        assert label.x == 2
        assert label.y == 2
        assert label.character == mock_character
        assert label.text == "Lvl: 5"

    def test_render_with_character(self, mock_renderer: Mock, mock_character: Mock) -> None:
        """Тест отрисовки с персонажем."""
        label = CharacterLevelLabel(x=7, y=7, character=mock_character)
        label.render(mock_renderer)
        mock_renderer.draw_text.assert_called_once_with("Lvl: 5", 7, 7)

    def test_render_no_character(self, mock_renderer: Mock) -> None:
        """Тест отрисовки без персонажа."""
        label = CharacterLevelLabel(x=8, y=8, character=None)
        label.render(mock_renderer)
        mock_renderer.draw_text.assert_called_once_with("Lvl: ?", 8, 8)


# ==================== Тесты ProgressBar ====================

class TestProgressBar:
    """Тесты для ProgressBar."""

    def test_initialization(self) -> None:
        """Тест инициализации ProgressBar."""
        bar = ProgressBar(x=0, y=0, width=10, current=50, maximum=100)
        assert bar.x == 0
        assert bar.y == 0
        assert bar.width == 10
        assert bar.current == 50
        assert bar.maximum == 100

    def test_render(self, mock_renderer: Mock) -> None:
        """Тест отрисовки ProgressBar."""
        bar = ProgressBar(x=1, y=1, width=20, current=30, maximum=100)
        bar.render(mock_renderer)
        # Проверяем, что draw_template был вызван
        mock_renderer.draw_template.assert_called_once()


# ==================== Тесты HealthBar ====================

class TestHealthBar:
    """Тесты для HealthBar."""

    def test_initialization(self, mock_character: Mock) -> None:
        """Тест инициализации HealthBar."""
        # Настраиваем мок персонажа для HealthBar
        mock_character.hp = 75
        mock_character.attributes.max_hp = 100
        
        bar = HealthBar(x=0, y=0, width=10, character=mock_character)
        assert bar.x == 0
        assert bar.y == 0
        assert bar.width == 10
        assert bar.character == mock_character
        assert bar.current == 75
        assert bar.maximum == 100

    def test_update_values(self, mock_character: Mock) -> None:
        """Тест обновления значений HealthBar."""
        # Настраиваем мок персонажа для HealthBar
        mock_character.hp = 75
        mock_character.attributes.max_hp = 100
        
        bar = HealthBar(x=1, y=1, width=15, character=mock_character)
        assert bar.current == 75
        assert bar.maximum == 100
        
        # Обновляем значения персонажа
        mock_character.hp = 50
        mock_character.attributes.max_hp = 150
        bar._update_values()
        assert bar.current == 50
        assert bar.maximum == 150

    def test_render(self, mock_renderer: Mock, mock_character: Mock) -> None:
        """Тест отрисовки HealthBar."""
        # Настраиваем мок персонажа для HealthBar
        mock_character.hp = 60
        mock_character.attributes.max_hp = 100
        
        bar = HealthBar(x=2, y=2, width=20, character=mock_character)
        bar.render(mock_renderer)
        mock_renderer.draw_template.assert_called_once()


# ==================== Тесты EnergyBar ====================

class TestEnergyBar:
    """Тесты для EnergyBar."""

    def test_initialization(self, mock_character: Mock) -> None:
        """Тест инициализации EnergyBar."""
        # Настраиваем мок персонажа для EnergyBar
        mock_character.energy = 40
        mock_character.attributes.max_energy = 80
        
        bar = EnergyBar(x=0, y=0, width=10, character=mock_character)
        assert bar.x == 0
        assert bar.y == 0
        assert bar.width == 10
        assert bar.character == mock_character
        assert bar.current == 40
        assert bar.maximum == 80

    def test_update_values(self, mock_character: Mock) -> None:
        """Тест обновления значений EnergyBar."""
        # Настраиваем мок персонажа для EnergyBar
        mock_character.energy = 40
        mock_character.attributes.max_energy = 80
        
        bar = EnergyBar(x=1, y=1, width=15, character=mock_character)
        assert bar.current == 40
        assert bar.maximum == 80
        
        # Обновляем значения персонажа
        mock_character.energy = 60
        mock_character.attributes.max_energy = 100
        bar._update_values()
        assert bar.current == 60
        assert bar.maximum == 100

    def test_render(self, mock_renderer: Mock, mock_character: Mock) -> None:
        """Тест отрисовки EnergyBar."""
        # Настраиваем мок персонажа для EnergyBar
        mock_character.energy = 30
        mock_character.attributes.max_energy = 100
        
        bar = EnergyBar(x=2, y=2, width=20, character=mock_character)
        bar.render(mock_renderer)
        mock_renderer.draw_template.assert_called_once()


# ==================== Тесты CharacterInfoPanel ====================

class TestCharacterInfoPanel:
    """Тесты для CharacterInfoPanel."""

    def test_initialization(self, mock_character: Mock) -> None:
        """Тест инициализации CharacterInfoPanel."""
        panel = CharacterInfoPanel(x=1, y=1, width=30, height=5, character=mock_character)
        assert panel.x == 1
        assert panel.y == 1
        assert panel.width == 30
        assert panel.height == 5
        assert panel.character == mock_character

    def test_set_character(self, mock_character: Mock) -> None:
        """Тест установки персонажа."""
        panel = CharacterInfoPanel(x=0, y=0, width=20, height=3, character=mock_character)
        # Создаем нового мок-персонажа
        new_character = Mock()
        new_character.name = "New Character"
        new_character.role = "mage"
        new_character.level = 2
        new_character.class_icon = "M"
        new_character.class_icon_color = "MAGENTA"
        new_character.hp = 60
        new_character.attributes.max_hp = 80
        new_character.energy = 40
        new_character.attributes.max_energy = 60
        
        panel.character = new_character
        assert panel.character == new_character

    def test_render(self, mock_renderer: Mock, mock_character: Mock) -> None:
        """Тест отрисовки панели."""
        # Настраиваем мок персонажа
        mock_character.hp = 80
        mock_character.attributes.max_hp = 100
        mock_character.energy = 50
        mock_character.attributes.max_energy = 100
        
        panel = CharacterInfoPanel(x=5, y=5, width=25, height=4, character=mock_character)
        panel.render(mock_renderer)
        # Проверяем, что render был вызван хотя бы один раз (для дочерних элементов)
        assert mock_renderer.draw_text.call_count >= 1 or mock_renderer.draw_template.call_count >= 1

    def test_update_size(self) -> None:
        """Тест обновления размеров панели."""
        # Создаем мок-персонажа
        mock_character = Mock()
        mock_character.name = "Resize Test"
        mock_character.role = "archer"
        mock_character.level = 4
        mock_character.class_icon = "A"
        mock_character.class_icon_color = "GREEN"
        mock_character.hp = 70
        mock_character.attributes.max_hp = 90
        mock_character.energy = 60
        mock_character.attributes.max_energy = 80
        
        panel = CharacterInfoPanel(x=0, y=0, width=20, height=3, character=mock_character)
        original_width = panel.width
        original_height = panel.height
        
        panel.update_size(30, 6)
        assert panel.width == 30
        assert panel.height == 6