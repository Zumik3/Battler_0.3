# game/events/render_data.py
"""
Данные для визуального отображения событий в текстовом интерфейсе.
"""
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Tuple



if TYPE_CHECKING:
    from game.ui.rendering.color_manager import Color

@dataclass
class RenderData:
    """Данные для визуального отображения событий в текстовом интерфейсе.
    
    Класс содержит информацию для рендеринга форматированного текста с использованием
    плейсхолдеров и стилизованных замен. Используется для унифицированного отображения
    игровых событий в UI компонентах (например, BattleLog).
    
    Attributes:
        template: Строка-шаблон, содержащая плейсхолдеры %1, %2, %3... для замены.
            Пример: "%1 наносит %2 урона %3"
        replacements: Словарь замен для плейсхолдеров. Ключ - строка плейсхолдера,
            значение - кортеж параметров отображения (текст, цвет, жирность, тусклость).
            
    Raises:
        ValueError: Если template пустая строка или replacements пустой словарь.
    
    Example:
        >>> from game.ui.rendering.color_manager import Color
        >>> render_data = RenderData(
        ...     template="%1 наносит %2 урона %3",
        ...     replacements={
        ...         "%1": ("Игрок", Color.GREEN, True, False),
        ...         "%2": ("25", Color.RED, True, False), 
        ...         "%3": ("орку", Color.YELLOW, False, False)
        ...     }
        ... )
    """
    
    template: str
    """Шаблон с плейсхолдерами %1, %2, %3..."""
    
    replacements: Dict[str, Tuple[str, 'Color', bool, bool]]
    """Словарь замен {placeholder: (text, color, bold, dim)}"""
    
    def __post_init__(self) -> None:
        """Валидация данных при инициализации.
        
        Проверяет, что template не пустая строка и replacements не пустой словарь.
        Гарантирует корректность данных для рендеринга.
        
        Raises:
            ValueError: Если template пустая или replacements пустой.
        """
        if not self.template:
            raise ValueError("Template cannot be empty")
        if not self.replacements:
            raise ValueError("Replacements cannot be empty")
    
    def get_formatted_text(self) -> str:
        """Возвращает текст с примененными заменами плейсхолдеров.
        
        Returns:
            Текстовая строка с замененными плейсхолдерами на соответствующий текст.
            
        Example:
            >>> render_data.get_formatted_text()
            "Игрок наносит 25 урона орку"
        """
        formatted_text = self.template
        for placeholder, (replacement_text, *_) in self.replacements.items():
            formatted_text = formatted_text.replace(placeholder, replacement_text)
        return formatted_text