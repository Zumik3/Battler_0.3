# game/ui/components/battle_components.py
"""Компоненты для экрана боя.

Содержит визуальные элементы для отображения игроков, врагов и лога боя.
"""

from typing import List, Optional, TYPE_CHECKING

from game.ui.rendering.color_manager import Color
from game.ui.rendering.renderable import Renderable

if TYPE_CHECKING:
    from game.ui.rendering.renderer import Renderer


class UnitPanel(Renderable):
    """Базовая панель для отображения одного юнита (игрока или монстра). Высота 1 строка."""

    def __init__(self, x: int, y: int, width: int, name: str, hp: int, max_hp: int,
                 mp: int = 0, max_mp: int = 0, is_player: bool = True):
        super().__init__(x, y)
        self.width = width
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.mp = mp
        self.max_mp = max_mp
        self.is_player = is_player
        # Заглушка для баффов/дебаффов
        self.status_effects: List[str] = []  # Например: ["Poison", "Shield"]

    def update_position(self, x: int, y: int) -> None:
        """Обновление позиции панели."""
        self.x = x
        self.y = y

    def update_stats(self, hp: int, max_hp: int, mp: int = 0, max_mp: int = 0) -> None:
        """Обновление статистики юнита."""
        self.hp = hp
        self.max_hp = max_hp
        self.mp = mp
        self.max_mp = max_mp

    def render(self, renderer: 'Renderer') -> None:
        """Отрисовка панели юнита в одну строку."""
        # Формат: [Имя] [HP Bar] [MP Bar] [Статусы]
        # Пример: Hero [#####.....] [***......] Poison
        try:
            # Рассчитываем доступную ширину
            available_width = self.width

            # Имя (минимум 8 символов)
            name_width = min(12, max(8, len(self.name)))
            name_part = self.name[:name_width].ljust(name_width)

            # Статусы (минимум 6 символов, максимум 15)
            status_str = " ".join(self.status_effects[:3])  # Показываем максимум 3 эффекта
            status_width = min(15, max(6, len(status_str)))
            status_part = status_str[:status_width].ljust(status_width)

            # Оставшаяся ширина для полосок HP и MP
            bars_width = available_width - name_width - status_width - 3  # 3 пробела

            # Если места мало, упрощаем
            if bars_width < 10:
                # Показываем только имя и HP в виде текста
                hp_text = f"{self.hp}/{self.max_hp}"
                simple_display = f"{name_part} {hp_text}".ljust(self.width)[:self.width]
                renderer.draw_text(
                    simple_display,
                    self.x,
                    self.y,
                    color=Color.GREEN if self.is_player else Color.RED
                )
                return

            # Делим оставшуюся ширину между HP и MP
            hp_bar_width = max(5, bars_width // 2)
            mp_bar_width = max(5, bars_width - hp_bar_width - 1)  # -1 для пробела

            # HP Bar
            hp_fill = int((self.hp / self.max_hp) * hp_bar_width) if self.max_hp > 0 else 0
            hp_bar = "#" * hp_fill + "." * (hp_bar_width - hp_fill)

            # MP Bar (если есть MP)
            mp_bar = ""
            if self.max_mp > 0:
                mp_fill = int((self.mp / self.max_mp) * mp_bar_width) if self.max_mp > 0 else 0
                mp_bar = " " + "*" * mp_fill + "." * (mp_bar_width - mp_fill)

            # Собираем строку
            display_line = f"{name_part} [{hp_bar}] [{mp_bar}] {status_part}".rstrip()
            # Обрезаем, если вышло за границы
            display_line = display_line[:self.width]

            # Определяем цвет
            color = Color.GREEN if self.is_player else Color.RED

            renderer.draw_text(display_line, self.x, self.y, color=color)

        except Exception as e:
            # В случае ошибки рисуем простую заглушку
            renderer.draw_text(
                f"{self.name} HP:{self.hp}/{self.max_hp}".ljust(self.width)[:self.width],
                self.x,
                self.y,
                color=Color.WHITE
            )


class PlayerUnitPanel(UnitPanel):
    """Панель для отображения одного игрока."""

    def __init__(self, x: int, y: int, width: int, name: str, hp: int, max_hp: int,
                 mp: int = 0, max_mp: int = 0):
        super().__init__(x, y, width, name, hp, max_hp, mp, max_mp, is_player=True)


class EnemyUnitPanel(UnitPanel):
    """Панель для отображения одного врага."""

    def __init__(self, x: int, y: int, width: int, name: str, hp: int, max_hp: int):
        # У врагов обычно нет MP
        super().__init__(x, y, width, name, hp, max_hp, 0, 0, is_player=False)


class GroupPanel(Renderable):
    """Панель для отображения группы юнитов (игроков или врагов)."""

    def __init__(self, x: int, y: int, width: int, height: int, title: str = ""):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.title = title
        self.unit_panels: List[UnitPanel] = []

    def add_unit_panel(self, unit_panel: UnitPanel) -> None:
        """Добавление панели юнита в группу."""
        self.unit_panels.append(unit_panel)

    def clear_unit_panels(self) -> None:
        """Очистка списка панелей юнитов."""
        self.unit_panels.clear()

    def update_size(self, total_width: int, total_height: int) -> None:
        """Обновление размеров группы."""
        # Размеры могут быть скорректированы внешним кодом
        pass

    def render(self, renderer: 'Renderer') -> None:
        """Отрисовка группы панелей."""
        # Рисуем рамку вокруг группы
        renderer.draw_box(self.x, self.y, self.width, self.height)

        # Рисуем заголовок, если он есть
        if self.title:
            title_x = self.x + max(0, (self.width - len(self.title)) // 2)
            renderer.draw_text(self.title, title_x, self.y, bold=True,
                             color=Color.CYAN if "Игроки" in self.title else Color.MAGENTA)

        # Отрисовываем панели юнитов
        for i, unit_panel in enumerate(self.unit_panels):
            if i >= self.height - 2:  # -2 для рамки и заголовка
                break  # Не помещаемся
            unit_panel.update_position(self.x + 1, self.y + 1 + i)
            unit_panel.render(renderer)


class BattleLog(Renderable):
    """Лог боя в нижней части экрана с прокруткой."""

    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__(x, y)
        self.width = width
        self.height = height
        # TODO: Получать реальные сообщения из игровой логики
        self.messages: List[str] = [
            "Битва начинается!",
            "Герой вступает в бой с Драконом.",
            "Дракон издает грозный рык.",
            "Герой атакует Дракона!",
            "Дракон получает 25 урона.",
            "Дракон атакует Героя!",
            "Герой получает 15 урона.",
            "Герой использует зелье лечения.",
            "Герой восстанавливает 30 HP.",
            "Дракон готовится к мощной атаке!",
            "Герой защищается.",
            "Мощная атака Дракона отражена!",
        ]
        self.scroll_offset = 0  # Смещение прокрутки (0 = последние сообщения внизу)

    def add_message(self, message: str) -> None:
        """Добавление сообщения в лог."""
        self.messages.append(message)
        # При добавлении нового сообщения сбрасываем прокрутку вниз
        self.scroll_offset = 0

    def scroll_up(self) -> None:
        """Прокрутка лога вверх."""
        # Максимальное смещение - это количество строк, которые не помещаются
        max_offset = max(0, len(self.messages) - (self.height - 2))
        self.scroll_offset = min(max_offset, self.scroll_offset + 1)

    def scroll_down(self) -> None:
        """Прокрутка лога вниз."""
        self.scroll_offset = max(0, self.scroll_offset - 1)

    def update_size(self, total_width: int, total_height: int) -> None:
        """Обновление размеров лога."""
        # Занимает всю ширину экрана
        self.width = max(10, total_width - 2)  # -2 для отступов
        # Высота динамическая, занимает всё оставшееся пространство
        # Предполагаем, что панели сверху занимают часть высоты
        # Этот расчет должен быть скорректирован в BattleScreen
        pass

    def render(self, renderer: 'Renderer') -> None:
        """Отрисовка лога боя."""
        # Рисуем рамку
        renderer.draw_box(self.x, self.y, self.width, self.height)

        # Заголовок лога
        log_title = "=== ЛОГ ==="
        title_x = self.x + max(0, (self.width - len(log_title)) // 2)
        renderer.draw_text(log_title, title_x, self.y, bold=True, color=Color.CYAN)

        # Отображаем сообщения с учетом прокрутки
        # Рассчитываем, сколько строк помещается (вычитаем 2 для рамки и заголовка)
        available_lines = self.height - 2
        # Начальный индекс с учетом прокрутки
        start_index = max(0, len(self.messages) - available_lines - self.scroll_offset)
        end_index = min(len(self.messages), start_index + available_lines)

        for i, message in enumerate(self.messages[start_index:end_index]):
            # Обрезаем сообщение, если оно длиннее области
            display_message = message[:self.width - 3]  # -3 для рамки и запаса
            renderer.draw_text(display_message, self.x + 1, self.y + 1 + i, dim=True)
