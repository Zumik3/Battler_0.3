# game/events/render_data.py
"""
Данные для визуального отображения событий в текстовом интерфейсе.
"""
from dataclasses import dataclass
from typing import Dict, Tuple

Color = int

@dataclass
class RenderData:
    """Данные для отрисовки шаблонного текста."""
    
    template: str  # Шаблон с плейсхолдерами %1, %2, %3...
    replacements: Dict[str, Tuple[str, Color, bool, bool]]  # {placeholder: (text, color, bold, dim)}
    
    def __post_init__(self):
        """Валидация данных."""
        if not self.template:
            raise ValueError("Template cannot be empty")
        if not self.replacements:
            raise ValueError("Replacements cannot be empty")