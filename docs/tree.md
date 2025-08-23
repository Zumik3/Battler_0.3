project-root/
├── game/                           # Основной пакет игры
│   ├── __init__.py
│   ├── config.py                   # Конфигурация игры
│   ├── protocols.py                # Протоколы и интерфейсы
│   ├── game_manager.py             # Менеджер игрового состояния (Singleton)
│   ├── results.py                  # Классы результатов действий
│   ├── logging_config.py           # Настройка логирования
│   ├── core/
│   │   └── context.py              # Игровой контекст и фабрика
│   ├── events/                     # Система событий
│   │   ├── __init__.py
│   │   ├── bus.py                  # Шина событий
│   │   └── character.py            # События персонажей
│   ├── entities/                   # Игровые сущности
│   │   ├── character.py            # Базовый класс персонажа
│   │   ├── player.py               # Класс игрока
│   │   ├── monster.py              # Класс монстра
│   │   └── properties/             # Система свойств персонажей
│   │       ├── __init__.py
│   │       ├── base.py             # Базовые классы свойств
│   │       ├── context.py          # Контекст свойств
│   │       ├── health.py           # Свойство здоровья
│   │       ├── energy.py           # Свойство энергии
│   │       ├── experience.py       # Свойство опыта
│   │       ├── level.py            # Свойство уровня
│   │       ├── combat.py           # Боевые свойства
│   │       ├── stats.py            # Базовые характеристики
│   │       └── stats_config.py     # Конфигурация характеристик
│   ├── factories/                  # Фабрики создания объектов
│   │   ├── __init__.py
│   │   ├── character_property_factory.py  # Базовая фабрика свойств
│   │   ├── player_factory.py       # Фабрика игроков
│   │   ├── player_property_factory.py     # Фабрика свойств игрока
│   │   ├── monster_factory.py      # Фабрика монстров
│   │   └── monster_property_factory.py    # Фабрика свойств монстра
│   ├── data/                       # Данные игры
│   │   ├── character_loader.py     # Загрузчик данных персонажей
│   │   └── characters/             # Данные персонажей
│   │       ├── player_classes/     # Классы игроков
│   │       │   ├── archer.json
│   │       │   ├── berserker.json
│   │       │   ├── healer.json
│   │       │   ├── mage.json
│   │       │   └── rogue.json
│   │       ├── monster_classes/    # Классы монстров
│   │       │   ├── goblin.json
│   │       │   ├── orc.json
│   │       │   ├── skeleton.json
│   │       │   ├── troll.json
│   │       │   └── wizard.json
│   │       └── names/              # Генерация имен
│   │           ├── adjectives.json
│   │           ├── nouns.json
│   │           ├── prefixes.json
│   │           └── suffixes.json
│   ├── naming/                     # Генерация имен
│   │   └── template_namer.py       # Генератор имен по шаблону
│   ├── mixins/                     # Миксины для повторного использования
│   │   ├── __init__.py
│   │   ├── logging_mixin.py        # Миксин логирования
│   │   └── ui_mixin.py             # Миксины UI
│   ├── ui/                         # Пользовательский интерфейс
│   │   ├── __init__.py
│   │   ├── screen_manager.py       # Менеджер экранов
│   │   ├── base_screen.py          # Базовый класс экрана
│   │   ├── main_screen.py          # Главный экран
│   │   ├── inventory_screen.py     # Экран инвентаря
│   │   ├── battle_screen.py        # Экран боя
│   │   ├── rendering/              # Система рендеринга
│   │   │   ├── __init__.py
│   │   │   ├── renderer.py         # Основной рендерер
│   │   │   ├── color_manager.py    # Управление цветами
│   │   │   ├── renderable.py       # Отрисовываемые элементы
│   │   │   └── template_renderer.py # Рендерер шаблонов
│   │   ├── command_system/         # Система команд
│   │   │   ├── __init__.py
│   │   │   ├── command.py          # Базовые классы команд
│   │   │   ├── command_renderer.py # Отрисовщик команд
│   │   │   └── screen_command_registry.py  # Реестр команд
│   │   ├── commands/               # Конкретные команды
│   │   │   ├── __init__.py
│   │   │   ├── common_commands.py  # Общие команды
│   │   │   ├── main_screen_commands.py     # Команды главного экрана
│   │   │   ├── inventory_commands.py       # Команды инвентаря
│   │   │   └── battle_commands.py  # Команды боя
│   │   ├── components/             # Компоненты UI
│   │   │   └── battle_components.py        # Компоненты боя
│   │   └── widgets/                # Переиспользуемые виджеты
│   │       ├── __init__.py
│   │       ├── labels.py           # Текстовые метки
│   │       ├── bars.py             # Прогресс-бары
│   │       └── character_card.py   # Карточка персонажа
│   └── results.py                  # Результаты действий
├── tests/                          # Тесты
│   ├── __init__.py
│   ├── test_game_manager.py        # Тесты GameManager
│   ├── test_character.py           # Тесты Character
│   ├── test_template_namer.py      # Тесты генератора имен
│   ├── test_command_system.py      # Тесты системы команд
│   └── test_ui/                    # Тесты UI
│       └── test_widgets.py         # Тесты виджетов
├── PROJECT_TODO.md                 # Список задач проекта
└── combined_source.txt             # Объединенный исходный код