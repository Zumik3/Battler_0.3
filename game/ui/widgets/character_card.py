# game/ui/widgets/character_card.py
"""Виджет для отображения сводной информации о персонаже.
Содержит имя, уровень, класс/роль, HP и энергию в компактном виде."""

from typing import Optional, TYPE_CHECKING, List

from game.ui.rendering.renderable import Renderable
from game.ui.rendering.renderer import Renderer
from game.ui.widgets.labels import CharacterNameLabel, CharacterLevelLabel, CharacterClassLabel
from game.ui.widgets.bars import HealthBar, EnergyBar

if TYPE_CHECKING:
    from game.entities.character import Character


class CharacterInfoPanel(Renderable):
    """Панель с информацией о персонаже, объединяющая несколько виджетов."""
    
    # Константы для макета
    CLASS_LABEL_X_OFFSET = 0
    NAME_LABEL_X_OFFSET = 5
    LEVEL_LABEL_X_OFFSET = -5  # Отрицательное значение для позиционирования справа
    MIN_NAME_LABEL_WIDTH = 10

    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 30,
        height: int = 5,
        character: Optional['Character'] = None,
        show_name: bool = True,
        show_class: bool = True,
        show_level: bool = True,
        show_health_bar: bool = True,
        show_energy_bar: bool = True
    ) -> None:
        """
        Инициализация панели информации о персонаже.

        Args:
            x: Координата X.
            y: Координата Y.
            width: Ширина панели.
            height: Высота панели.
            character: Объект персонажа для отображения.
            show_class: Показывать ли метку класса/роли.
            show_name: Показывать ли метку имени.
            show_level: Показывать ли метку уровня.
            show_health_bar: Показывать ли полосу здоровья.
            show_energy_bar: Показывать ли полосу энергии.
        """
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.character = character
        
        # Флаги отображения компонентов
        self.show_name = show_name
        self.show_class = show_class
        self.show_level = show_level
        self.show_health_bar = show_health_bar
        self.show_energy_bar = show_energy_bar

        # Создаем дочерние виджеты (они могут быть неактивны, если show_* = False)
        self.class_label: Optional[CharacterClassLabel] = None
        self.name_label: Optional[CharacterNameLabel] = None
        self.level_label: Optional[CharacterLevelLabel] = None
        self.health_bar: Optional[HealthBar] = None
        self.energy_bar: Optional[EnergyBar] = None
        
        # Инициализируем виджеты в зависимости от флагов
        self._initialize_widgets()
        
        # Если передан персонаж, устанавливаем его для всех виджетов
        if self.character:
            self.set_character(self.character)

    def _initialize_widgets(self) -> None:
        """Инициализировать дочерние виджеты в зависимости от флагов отображения."""
        if self.show_name:
            self.name_label = CharacterNameLabel(
                x=self.x + self.NAME_LABEL_X_OFFSET, 
                y=self.y, 
                max_width=max(self.MIN_NAME_LABEL_WIDTH, self.width - self.NAME_LABEL_X_OFFSET + self.LEVEL_LABEL_X_OFFSET)
            )

        if self.show_class:
            self.class_label = CharacterClassLabel(x=self.x + self.CLASS_LABEL_X_OFFSET, y=self.y)
            
        if self.show_level:
            self.level_label = CharacterLevelLabel(x=self.x + self.width + self.LEVEL_LABEL_X_OFFSET, y=self.y)
            
        if self.show_health_bar:
            self.health_bar = HealthBar(x=self.x, y=self.y + 1, width=self.width)
            
        if self.show_energy_bar:
            self.energy_bar = EnergyBar(x=self.x, y=self.y + 2, width=self.width)

    def set_character(self, character: Optional['Character']) -> None:
        """
        Установить персонажа для отображения во всех дочерних виджетах.

        Args:
            character: Объект персонажа или None.
        """
        self.character = character
        
        # Устанавливаем персонажа только для активных виджетов
        if self.class_label and self.show_class:
            self.class_label.set_character(character)
        if self.name_label and self.show_name:
            self.name_label.set_character(character)
        if self.level_label and self.show_level:
            self.level_label.set_character(character)
        if self.health_bar and self.show_health_bar:
            self.health_bar.set_character(character)
        if self.energy_bar and self.show_energy_bar:
            self.energy_bar.set_character(character)

    def update_size(self, width: int, height: int) -> None:
        """
        Обновить размеры панели и пересчитать позиции дочерних элементов.

        Args:
            width: Новая ширина панели.
            height: Новая высота панели.
        """
        self.width = width
        self.height = height
        
        # Пересчитываем позиции активных дочерних виджетов
        if self.class_label and self.show_class:
            self.class_label.x = self.x + self.CLASS_LABEL_X_OFFSET
            self.class_label.y = self.y
            
        if self.name_label and self.show_name:
            self.name_label.x = self.x + self.NAME_LABEL_X_OFFSET
            self.name_label.y = self.y
            # Обновляем максимальную ширину имени с учетом новых размеров
            calculated_max_width = self.width - self.NAME_LABEL_X_OFFSET + self.LEVEL_LABEL_X_OFFSET
            self.name_label.max_width = max(self.MIN_NAME_LABEL_WIDTH, calculated_max_width)
            
        if self.level_label and self.show_level:
            self.level_label.x = self.x + self.width + self.LEVEL_LABEL_X_OFFSET  # Позиционируем уровень справа
            self.level_label.y = self.y
            
        if self.health_bar and self.show_health_bar:
            self.health_bar.x = self.x
            self.health_bar.y = self.y + 1
            self.health_bar.width = self.width
            
        if self.energy_bar and self.show_energy_bar:
            self.energy_bar.x = self.x
            self.energy_bar.y = self.y + 2
            self.energy_bar.width = self.width

    def render(self, renderer: Renderer) -> None:
        """
        Отрисовка панели информации о персонаже.
        
        Args:
            renderer: Рендерер для отрисовки.
        """
        # Отрисовываем только активные дочерние виджеты
        renderable_widgets: List[Renderable] = []
        
        if self.class_label and self.show_class:
            renderable_widgets.append(self.class_label)
        if self.name_label and self.show_name:
            renderable_widgets.append(self.name_label)
        if self.level_label and self.show_level:
            renderable_widgets.append(self.level_label)
        if self.health_bar and self.show_health_bar:
            renderable_widgets.append(self.health_bar)
        if self.energy_bar and self.show_energy_bar:
            renderable_widgets.append(self.energy_bar)
            
        # Отрисовываем все активные виджеты
        for widget in renderable_widgets:
            widget.render(renderer)
