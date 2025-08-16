# game/ui/widgets/bars.py
"""Прогресс-бары для отображения различных параметров (HP, Energy и т.д.).
Эти компоненты могут использоваться в различных частях интерфейса,
например, на экране боя, экране персонажа и т.д."""

from typing import Optional, TYPE_CHECKING, Dict, Tuple
from abc import ABC, abstractmethod

from game.ui.rendering.renderable import Renderable
from game.ui.rendering.renderer import Renderer
from game.ui.rendering.color_manager import Color

if TYPE_CHECKING:
    from game.entities.character import Character


class ProgressBar(Renderable, ABC):
    """Базовый класс для отрисовки прогресс-бара с использованием шаблонов."""

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 20,
        character: Optional['Character'] = None
    ) -> None:
        """
        Инициализация базового прогресс-бара.

        Args:
            x: Координата X.
            y: Координата Y.
            width: Ширина прогресс-бара в символах.
            character: Объект персонажа для отслеживания значений.
        """
        super().__init__(x, y)
        self.width = width
        self.character = character

    @abstractmethod
    def _get_current_value(self) -> int:
        """Получить текущее значение из персонажа."""
        pass

    @abstractmethod
    def _get_max_value(self) -> int:
        """Получить максимальное значение из персонажа."""
        pass

    @abstractmethod
    def _get_fill_color(self) -> Color:
        """Получить цвет заполненной части прогресс-бара."""
        pass

    @abstractmethod
    def _get_empty_color(self) -> Color:
        """Получить цвет пустой части прогресс-бара."""
        pass

    def set_character(self, character: Optional['Character']) -> None:
        """
        Установить персонажа для отслеживания значений.

        Args:
            character: Объект персонажа или None.
        """
        self.character = character

    def _create_progress_template(
        self,
        filled_count: int,
        empty_count: int
    ) -> Tuple[str, Dict[str, Tuple[str, Color, bool, bool]]]:
        """
        Создать шаблон и словарь замен для отрисовки прогресс-бара.

        Args:
            filled_count: Количество заполненных символов.
            empty_count: Количество пустых символов.

        Returns:
            Кортеж (шаблон, словарь_замен).
        """
        # Создаем строки заполнения
        filled_part = "█" * filled_count  # Полностью заполненные символы
        empty_part = "░" * empty_count    # Пустые символы

        # Создаем шаблон
        # %1 - открывающая скобка, %2 - заполненная часть, %3 - пустая часть, %4 - закрывающая скобка
        template = "%1%2%3%4"
        
        replacements = {
            "1": ("[", Color.WHITE, False, False),      # Открывающая скобка
            "2": (filled_part, self._get_fill_color(), False, False),  # Заполненная часть
            "3": (empty_part, self._get_empty_color(), False, False),  # Пустая часть
            "4": ("]", Color.WHITE, False, False)       # Закрывающая скобка
        }
        
        return template, replacements

    def render(self, renderer: Renderer) -> None:
        """Отрисовка прогресс-бара с использованием шаблона."""
        template, replacements = self._get_template_and_replacements()
        renderer.draw_template(template, replacements, self.x, self.y)

    def _get_template_and_replacements(self) -> Tuple[str, Dict[str, Tuple[str, Color, bool, bool]]]:
        """
        Создать шаблон и словарь замен для отрисовки прогресс-бара.

        Returns:
            Кортеж (шаблон, словарь_замен).
        """
        # Получаем значения из персонажа
        if self.character:
            current_value = self._get_current_value()
            max_value = self._get_max_value()
        else:
            current_value = 0
            max_value = 1

        # Рассчитываем количество заполненных и пустых символов
        if max_value <= 0:
            filled_count = 0
        else:
            # Используем пропорцию: filled_count / self.width = current_value / max_value
            filled_count = int((current_value / max_value) * self.width)
        
        # Убеждаемся, что значения в допустимых пределах
        filled_count = max(0, min(filled_count, self.width))
        empty_count = self.width - filled_count

        # Используем общий метод для создания шаблона
        return self._create_progress_template(filled_count, empty_count)


class HealthBar(ProgressBar):
    """Прогресс-бар для отображения здоровья (HP)."""

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 20,
        character: Optional['Character'] = None
    ) -> None:
        """
        Инициализация прогресс-бара здоровья.

        Args:
            x: Координата X.
            y: Координата Y.
            width: Ширина прогресс-бара в символах.
            character: Объект персонажа для отслеживания HP.
        """
        super().__init__(x, y, width, character)

    def _get_current_value(self) -> int:
        """Получить текущее значение HP из персонажа."""
        if self.character:
            return getattr(self.character, 'hp', 0)
        return 0

    def _get_max_value(self) -> int:
        """Получить максимальное значение HP из персонажа."""
        if self.character:
            attributes = getattr(self.character, 'attributes', None)
            if attributes:
                # Используем consistent fallback: 1 как минимальное значение
                return max(1, getattr(attributes, 'max_hp', 1))
        # Если персонажа нет или атрибуты не определены, возвращаем 1 как fallback
        return 1

    def _get_fill_color(self) -> Color:
        """Получить цвет заполненной части для HP (зеленый)."""
        if not self.character:
            return Color.GREEN
            
        # Получаем значения для расчета цвета
        current = self._get_current_value()
        max_val = self._get_max_value()
        
        ratio: float = 0
        if max_val > 0:
            ratio = current / max_val
            
        if ratio < 0.25:
            return Color.RED
        elif ratio < 0.5:
            return Color.YELLOW
        else:
            return Color.GREEN

    def _get_empty_color(self) -> Color:
        """Получить цвет пустой части для HP (темно-серый/серый)."""
        return Color.GRAY


class EnergyBar(ProgressBar):
    """Прогресс-бар для отображения энергии (Energy/MP)."""

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 20,
        character: Optional['Character'] = None
    ) -> None:
        """
        Инициализация прогресс-бара энергии.

        Args:
            x: Координата X.
            y: Координата Y.
            width: Ширина прогресс-бара в символах.
            character: Объект персонажа для отслеживания энергии.
        """
        super().__init__(x, y, width, character)

    def _get_current_value(self) -> int:
        """Получить текущее значение энергии из персонажа."""
        if self.character:
            return getattr(self.character, 'energy', 0)
        return 0

    def _get_max_value(self) -> int:
        """Получить максимальное значение энергии из персонажа."""
        if self.character:
            attributes = getattr(self.character, 'attributes', None)
            if attributes:
                # Используем consistent fallback: 0 как минимальное значение (если энергия не используется)
                return max(0, getattr(attributes, 'max_energy', 0))
        # Если персонажа нет или атрибуты не определены, возвращаем 0 как fallback
        return 0

    def _get_fill_color(self) -> Color:
        """Получить цвет заполненной части для энергии (синий)."""
        return Color.BLUE

    def _get_empty_color(self) -> Color:
        """Получить цвет пустой части для энергии (темно-серый/серый)."""
        return Color.GRAY
