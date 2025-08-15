# game/ui/main_screen.py
"""
Главный экран игры.
Отображает главное меню с возможностью перехода в бой или инвентарь,
а также выход из игры.
"""
import curses
# --- ДОБАВЛЯЕМ ИМПОРТ МИКСИНА ---
from game.ui.mixins import StandardLayoutMixin
# --------------------------------
from game.ui.base_screen import BaseScreen
from game.ui.rendering.renderable import Text, Separator
from game.ui.rendering.color_manager import Color

# --- НАСЛЕДУЕМСЯ ОТ StandardLayoutMixin ---
class MainScreen(BaseScreen, StandardLayoutMixin):
    """Главный экран игры."""

    def _setup_elements(self) -> None:
        """Настройка элементов экрана."""
        # УБИРАЕМ старый заголовок и разделитель, так как они теперь в миксине
        self.elements = [
            # Основные кнопки (визуальное отображение)
            # Смещаем Y на +2, так как шапка занимает первые 2 строки
            Text("[1] Начать бой", 5, 2, color=Color.GREEN, bold=True),
            Text("[2] Инвентарь", 5, 3, color=Color.YELLOW),
            Text("[3] Настройки", 5, 4, color=Color.MAGENTA, dim=True),
            # Separator(6, color=Color.BLUE), # Убираем старый разделитель
            # Кнопка выхода
            Text("[q] Выйти из игры", 20, 6, color=Color.RED, dim=True),
            # Информационное сообщение
            Text("Используйте клавиши 1, 2, 3 для навигации", 2, 8, dim=True),
            Text("Нажмите 'q' для выхода", 2, 9, dim=True)
            # Нижний разделитель и команды теперь тоже из миксина
        ]

    def _setup_commands(self) -> None:
        """Настройка дополнительных команд экрана."""
        # Все команды добавятся автоматически из реестра!
        pass

    # --- ОБНОВЛЯЕМ МЕТОД render ---
    def render(self, stdscr: curses.window) -> None:
        """Отрисовка экрана."""
        self.renderer.clear()
        
        # Отрисовка стандартного макета (шапка + подвал)
        self.render_standard_layout("=== ГЛАВНОЕ МЕНЮ ===")
        
        # Отрисовка основных элементов
        for element in self.elements:
            element.render(self.renderer)
            
        self.renderer.refresh() # Не забываем refresh в конце конкретного render

    def _handle_unregistered_key(self, key: int) -> None:
        """Обработка незарегистрированных клавиш."""
        pass
