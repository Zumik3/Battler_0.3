# game/ui/widgets/labels.py
"""Базовые текстовые метки для отображения информации.

Эти компоненты могут использоваться в различных частях интерфейса,
например, для отображения имени, уровня, класса персонажа и другой информации.
"""

from typing import Optional, TYPE_CHECKING, Dict, Tuple

from game.ui.rendering.renderable import Renderable
from game.ui.rendering.renderer import Renderer
from game.ui.rendering.color_manager import Color

if TYPE_CHECKING:
    from game.entities.character import Character


class TextLabel(Renderable):
    """Базовая текстовая метка."""

    def __init__(
        self, 
        x: int = 0, 
        y: int = 0, 
        text: str = "", 
        color: Color = Color.DEFAULT,
        bold: bool = False,
        dim: bool = False
    ) -> None:
        """
        Инициализация текстовой метки.

        Args:
            x: Координата X.
            y: Координата Y.
            text: Отображаемый текст.
            color: Цвет текста.
            bold: Жирный шрифт.
            dim: Тусклый шрифт.
        """
        super().__init__(x, y)
        self.text = text
        self.color = color
        self.bold = bold
        self.dim = dim
        

    def render(self, renderer: Renderer) -> None:
        """Отрисовка текстовой метки."""
        if self.text:
            renderer.draw_text(self.text, self.x, self.y, self.bold, self.dim, self.color)


class CharacterNameLabel(TextLabel):
    """Метка для отображения имени персонажа."""

    def __init__(
        self,
        character: Optional['Character'], 
        x: int = 0, 
        y: int = 0,
        max_width: int = 0,
        color: Color = Color.DEFAULT,
        bold: bool = False,
        dim: bool = False
    ) -> None:
        """
        Инициализация метки имени персонажа.

        Args:
            x: Координата X.
            y: Координата Y.
            character: Объект персонажа, имя которого нужно отобразить.
            max_width: Максимальная ширина текста (для обрезки/усечения).
            color: Цвет текста.
            bold: Жирный шрифт.
            dim: Тусклый шрифт.
        """
        # Инициализируем с пустым текстом, он будет обновлен в update_from_character
        super().__init__(x, y, "", color, bold, dim)
        self.character = character
        self.max_width = max_width
        self._update_from_character()

    def _update_from_character(self) -> None:
        """Обновить текст метки из данных персонажа."""
        if self.character:
            name = getattr(self.character, 'name', 'Unknown')
            if self.max_width and len(name) > self.max_width:
                # Простое усечение, можно улучшить (например, добавить "...")
                self.text = name[:self.max_width]
            else:
                self.text = name
        else:
            self.text = "Unknown"


class TemplatedTextLabel(TextLabel):
    """Базовая метка для отрисовки текста с использованием шаблонов и цветов."""
    
    def __init__(self, x: int = 0, y: int = 0) -> None:
        """
        Инициализация метки с шаблонами.

        Args:
            x: Координата X.
            y: Координата Y.
        """
        super().__init__(x, y)

    def _create_bracketed_template(
        self, 
        content: str, 
        content_color: Color = Color.DEFAULT,
        bracket_color: Color = Color.WHITE
    ) -> Tuple[str, Dict[str, Tuple[str, Color, bool, bool]]]:
        """
        Создать шаблон вида [content] с разными цветами для скобок и содержимого.

        Args:
            content: Содержимое внутри скобок.
            content_color: Цвет содержимого.
            bracket_color: Цвет скобок.

        Returns:
            Кортеж (шаблон, словарь_замен).
        """
        return (
            "%1%2%3",
            {
                "1": ("[", bracket_color, False, False),
                "2": (content, content_color, False, False),
                "3": ("]", bracket_color, False, False)
            }
        )

    def render(self, renderer: Renderer) -> None:
        """Отрисовка текста с использованием шаблона."""
        template, replacements = self._get_template_and_replacements()
        renderer.draw_template(template, replacements, self.x, self.y)
        
    def _get_template_and_replacements(self) -> Tuple[str, Dict[str, Tuple[str, Color, bool, bool]]]:
        """
        Получить шаблон и словарь замен для отрисовки.
        
        Returns:
            Кортеж (шаблон, словарь_замен).
        """
        raise NotImplementedError("Subclasses must implement _get_template_and_replacements")


class CharacterClassLabel(TemplatedTextLabel):
    """Метка для отображения класса/роли персонажа в формате [Роль]."""

    def __init__(
        self,
        character: Optional['Character'], 
        x: int = 0, 
        y: int = 0, 
    ) -> None:
        """
        Инициализация метки класса персонажа.

        Args:
            x: Координата X.
            y: Координата Y.
            character: Объект персонажа, класс которого нужно отобразить.
        """
        super().__init__(x, y)
        self.character = character
        self.text = "?"
        self.color = Color.DEFAULT
        self._update_from_character()

    def _update_from_character(self) -> None:
        """Обновить текст метки из данных персонажа."""
        if self.character:
            self.text = getattr(self.character, 'class_icon', "?")
            color_str = getattr(self.character, 'class_icon_color', "")
            
            # Конвертируем строку в enum Color
            if color_str:
                try:
                    self.color = Color[color_str.upper()]
                except (KeyError, AttributeError):
                    self.color = Color.DEFAULT
            else:
                self.color = Color.DEFAULT
        else:
            self.text = "?"
            self.color = Color.DEFAULT

    def _get_template_and_replacements(self) -> Tuple[str, Dict[str, Tuple[str, Color, bool, bool]]]:
        """Определяем шаблон и замены для роли."""
        return self._create_bracketed_template(self.text, self.color)


class CharacterLevelLabel(TemplatedTextLabel):
    """Метка для отображения уровня персонажа в формате [1]."""

    def __init__(
        self,
        character: Optional['Character'], 
        x: int = 0, 
        y: int = 0, 
    ) -> None:
        """
        Инициализация метки уровня персонажа.

        Args:
            x: Координата X.
            y: Координата Y.
            character: Объект персонажа, уровень которого нужно отобразить.
        """
        super().__init__(x, y)
        self.character = character
        self.text = "1"
        self._update_from_character()

    def _update_from_character(self) -> None:
        """Обновить текст метки из данных персонажа."""
        if self.character and hasattr(self.character, 'level'):
            # Получаем уровень из свойства level
            level_value = getattr(self.character.level, 'level', 1)
            self.text = str(level_value)
        else:
            self.text = "1"

    def _get_template_and_replacements(self) -> Tuple[str, Dict[str, Tuple[str, Color, bool, bool]]]:
        """Определяем шаблон и замены для уровня."""
        return self._create_bracketed_template(self.text, Color.YELLOW)