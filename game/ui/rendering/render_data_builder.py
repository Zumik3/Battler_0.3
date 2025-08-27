# game/ui/rendering/render_data_builder.py
"""Строитель для упрощения создания RenderData."""

from typing import Dict, Tuple, Optional, TYPE_CHECKING
from game.ui.rendering.color_manager import Color

from game.events.render_data import RenderData

if TYPE_CHECKING:
    from game.entities.character import Character


class RenderDataBuilder:
    """
    Строитель для упрощения и структурирования создания RenderData.
    
    Позволяет поэтапно формировать шаблон сообщения и его замены,
    делая код более читаемым. Плейсхолдеры генерируются автоматически.
    """

    def __init__(self, base_template: str = "") -> None:
        """
        Инициализирует строитель.
        
        Args:
            base_template (str): Базовый шаблон. Можно начать с пустой строки
                                 и строить его по частям, или задать сразу.
        """
        self._parts: list[str] = []  # Части шаблона
        self._replacements: Dict[str, Tuple[str, str, bool, bool]] = {}
        self._counter: int = 1
        
        if base_template:
            self._parts.append(base_template)

    def add_text(self, text: str) -> 'RenderDataBuilder':
        """
        Добавляет обычный текст в шаблон как статическую часть.
        Такой текст не будет заменяться.
        
        Args:
            text (str): Текст для добавления.
            
        Returns:
            RenderDataBuilder: Этот же экземпляр для цепочки вызовов.
        """
        self._parts.append(text)
        return self

    self._replacements: Dict[str, Tuple[str, Color, bool, bool]] = {}
        self._counter: int = 1
        
        if base_template:
            self._parts.append(base_template)

    def add_text(self, text: str) -> 'RenderDataBuilder':
        """
        Добавляет обычный текст в шаблон как статическую часть.
        Такой текст не будет заменяться.
        
        Args:
            text (str): Текст для добавления.
            
        Returns:
            RenderDataBuilder: Этот же экземпляр для цепочки вызовов.
        """
        self._parts.append(text)
        return self

    def add_styled_text(self, text: str, color: Color = Color.DEFAULT, bold: bool = False, underline: bool = False) -> 'RenderDataBuilder':
        """
        Добавляет стилизованный текст и автоматически регистрирует его замену.
        Создает плейсхолдер в формате %N.
        
        Args:
            text (str): Текст.
            color (Color): Цвет (например, Color.RED).
            bold (bool): Жирный шрифт.
            underline (bool): Подчеркнутый шрифт.
            
        Returns:
            RenderDataBuilder: Этот же экземпляр для цепочки вызовов.
        """
        placeholder = str(self._counter)
        self._counter += 1
            
        self._parts.append(f"%{placeholder}")
        self._replacements[placeholder] = (text, color, bold, underline)
        return self

    def add_replacement(self, text: str, color: Color = Color.DEFAULT, bold: bool = False, underline: bool = False) -> str:
        """
        Регистрирует замену и возвращает соответствующий плейсхолдер.
        Полезно, если нужно вставить плейсхолдер вручную в шаблон.
        
        Args:
            text (str): Текст для подстановки.
            color (Color): Цвет.
            bold (bool): Жирный шрифт.
            underline (bool): Подчеркнутый шрифт.
            
        Returns:
            str: Сгенерированный плейсхолдер (например, "3").
        """
        placeholder = str(self._counter)
        self._counter += 1
        
        self._replacements[placeholder] = (text, color, bold, underline)
        return placeholder

    def build(self) -> RenderData:
        """
        Создаёт объект RenderData из собранных частей.
        
        Returns:
            RenderData: Готовый объект для использования в событиях.
        """
        final_template = "".join(self._parts)
        return RenderData(template=final_template, replacements=self._replacements)

    # --- Специализированные методы для частых случаев ---
    
    def add_character_name(self, character: 'Character', bold: bool = True) -> 'RenderDataBuilder':
        """
        Добавляет имя персонажа, автоматически определяя цвет в зависимости от типа персонажа.
        Игроки и монстры могут иметь разные цвета.
        
        Args:
            character (Character): Объект персонажа.
            bold (bool): Должно ли имя отображаться жирным шрифтом. По умолчанию True.
            
        Returns:
            RenderDataBuilder: Этот же экземпляр для цепочки вызовов.
        """
        
        if character.is_player:
            color = Color.GREEN
        else:
            color = Color.BLUE
        
        return self.add_styled_text(character.name, color, bold, False)

    # Оставляем старый метод для обратной совместимости или специальных случаев
    def add_character_name_simple(self, name: str, color: Color = Color.DEFAULT, bold: bool = True) -> 'RenderDataBuilder':
        """
        Добавляет имя персонажа с явно заданным цветом.
        (Старый метод для совместимости или особых случаев)
        """
        return self.add_styled_text(name, color, bold, False)

    def add_replacement(self, text: str, color: str = "", bold: bool = False, underline: bool = False) -> str:
        """
        Регистрирует замену и возвращает соответствующий плейсхолдер.
        Полезно, если нужно вставить плейсхолдер вручную в шаблон.
        
        Args:
            text (str): Текст для подстановки.
            color (str): Цвет.
            bold (bool): Жирный шрифт.
            underline (bool): Подчеркнутый шрифт.
            
        Returns:
            str: Сгенерированный плейсхолдер (например, "3").
        """
        placeholder = str(self._counter)
        self._counter += 1
        
        self._replacements[placeholder] = (text, color, bold, underline)
        return placeholder

    def build(self) -> RenderData:
        """
        Создаёт объект RenderData из собранных частей.
        
        Returns:
            RenderData: Готовый объект для использования в событиях.
        """
        final_template = "".join(self._parts)
        return RenderData(template=final_template, replacements=self._replacements)

    # --- Специализированные методы для частых случаев ---
    
    def add_character_name(self, character: 'Character', bold: bool = True) -> 'RenderDataBuilder':
        """
        Добавляет имя персонажа, автоматически определяя цвет в зависимости от типа персонажа.
        Игроки и монстры могут иметь разные цвета.
        
        Args:
            character (Character): Объект персонажа.
            bold (bool): Должно ли имя отображаться жирным шрифтом. По умолчанию True.
            
        Returns:
            RenderDataBuilder: Этот же экземпляр для цепочки вызовов.
        """
        
        if character.is_player:
            color = Color.GREEN
        else:
            color = Color.BLUE
        
        return self.add_styled_text(character.name, color, bold, False)

    # Оставляем старый метод для обратной совместимости или специальных случаев
    def add_character_name_simple(self, name: str, color: str = "", bold: bool = True) -> 'RenderDataBuilder':
        """
        Добавляет имя персонажа с явно заданным цветом.
        (Старый метод для совместимости или особых случаев)
        """
        return self.add_styled_text(name, color, bold, False)

    def add_damage_value(self, damage: int) -> 'RenderDataBuilder':
        """Добавляет значение урона (обычно красное и жирное)."""
        return self.add_styled_text(str(damage), Color.RED, True, False)

    def add_heal_value(self, heal: int) -> 'RenderDataBuilder':
        """Добавляет значение лечения (обычно зеленое и жирное)."""
        return self.add_styled_text(str(heal), Color.GREEN, True, False)

    def add_exp_value(self, exp: int) -> 'RenderDataBuilder':
        """Добавляет значение опыта (обычно желтое и жирное)."""
        return self.add_styled_text(str(exp), Color.YELLOW, True, False)
