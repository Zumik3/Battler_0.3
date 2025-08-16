# game/ui/widgets/labels.py
"""Базовые текстовые метки для отображения информации.
Эти компоненты могут использоваться в различных частях интерфейса,
например, для отображения имени, уровня, класса персонажа и другой информации."""

from typing import Optional, TYPE_CHECKING, Any, Dict, Tuple

from game.ui.rendering.renderable import Renderable
from game.ui.rendering.renderer import Renderer
from game.ui.rendering.color_manager import Color

if TYPE_CHECKING:
    from game.entities.character import Character


def _get_character_role_icon(character: 'Character') -> str:
    """
    Получить первую букву роли или класса персонажа для отображения в виде иконки.
    
    Args:
        character: Объект персонажа.
        
    Returns:
        Первая буква роли или класса персонажа, или '?' если не удалось определить.
    """
    # Пытаемся получить роль
    role = getattr(character, 'role', "?")
    role_str = str(role)
    return role_str[0] if role_str else '?'


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
        x: int = 0, 
        y: int = 0, 
        character: Optional['Character'] = None,
        max_width: Optional[int] = None,
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

    def set_character(self, character: Optional['Character']) -> None:
        """
        Установить персонажа для отображения и обновить текст метки.

        Args:
            character: Объект персонажа или None.
        """
        self.character = character
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
        x: int = 0, 
        y: int = 0, 
        character: Optional['Character'] = None,
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

    def set_character(self, character: Optional['Character']) -> None:
        """
        Установить персонажа для отображения.

        Args:
            character: Объект персонажа или None.
        """
        self.character = character

    def _get_template_and_replacements(self) -> Tuple[str, Dict[str, Tuple[str, Color, bool, bool]]]:
        """Определяем шаблон и замены для роли."""
        
        if self.character:
            role = _get_character_role_icon(self.character)
        else:
            role = '?'

        return self._create_bracketed_template(str(role), Color.CYAN)


class CharacterLevelLabel(TemplatedTextLabel):
    """Метка для отображения уровня персонажа в формате [1]."""

    def __init__(
        self, 
        x: int = 0, 
        y: int = 0, 
        character: Optional['Character'] = None,
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

    def set_character(self, character: Optional['Character']) -> None:
        """
        Установить персонажа для отображения.

        Args:
            character: Объект персонажа или None.
        """
        self.character = character

    def _get_template_and_replacements(self) -> Tuple[str, Dict[str, Tuple[str, Color, bool, bool]]]:
        """Определяем шаблон и замены для уровня."""
        if self.character:
            level = getattr(self.character, 'level', 1)
        else:
            level = 1

        return self._create_bracketed_template(str(level), Color.YELLOW)
