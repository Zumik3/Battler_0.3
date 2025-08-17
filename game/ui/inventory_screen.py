# game/ui/inventory_screen.py
"""
Экран инвентаря.
Отображает содержимое инвентаря игрока.
"""
import curses
# --- ДОБАВЛЯЕМ ИМПОРТ МИКСИНА ---
from game.mixins.ui_mixin import StandardLayoutMixin
# --------------------------------
from game.ui.base_screen import BaseScreen
from game.ui.rendering.renderable import Text, Separator
from game.ui.rendering.color_manager import Color

# --- НАСЛЕДУЕМСЯ ОТ StandardLayoutMixin ---
class InventoryScreen(BaseScreen, StandardLayoutMixin):
    """Экран инвентаря."""

    def _setup_elements(self) -> None:
        """Настройка элементов экрана."""
        # УБИРАЕМ старый заголовок и разделитель
        self.elements = [
            # Предметы инвентаря (смещаем Y на +2)
            Text("• Меч (+10 ATK)", 2, 2, color=Color.WHITE),           # Смещаем Y
            Text("• Зелье лечения", 2, 3, color=Color.GREEN, dim=True), # Смещаем Y
            Text("• Ключ от сундука", 2, 4, color=Color.CYAN, dim=True), # Смещаем Y
            Text("• Свиток телепортации", 2, 5, color=Color.MAGENTA, dim=True), # Смещаем Y
            # Separator(7, "-", 40, Color.WHITE, dim=True), # Убираем старый разделитель
            # Статистика (смещаем Y)
            Text("Всего предметов: 4", 2, 7, dim=True), # Смещаем Y
            Text("Занято: 4/20", 2, 8, dim=True),       # Смещаем Y
            # Separator(10, color=Color.YELLOW), # Убираем старый разделитель
        ]

    def _setup_commands(self) -> None:
        """Настройка дополнительных команд экрана."""
        # Команды из реестра добавятся автоматически!
        # Здесь можно добавить специфичные для этого экрана команды
        pass

    # --- ОБНОВЛЯЕМ МЕТОД render ---
    def render(self, stdscr: curses.window) -> None:
        """Отрисовка экрана."""
        self.renderer.clear()
        
        # Отрисовка стандартного макета
        self.render_standard_layout("=== ИНВЕНТАРЬ ===")
        
        # Отрисовка основных элементов
        for element in self.elements:
            element.render(self.renderer)
            
        self.renderer.refresh() # Не забываем refresh

    def _handle_unregistered_key(self, key: int) -> None:
        """Обработка незарегистрированных клавиш."""
        pass
