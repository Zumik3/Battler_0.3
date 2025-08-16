# game/config.py
"""Основные настройки игры."""

from dataclasses import dataclass, field
from pathlib import Path
import json
import os
from typing import Any, Dict


@dataclass
class ExperienceSettings:
    """Настройки системы опыта."""

    formula_base: int = 100
    formula_multiplier: float = 1.5


@dataclass
class CombatSettings:
    """Настройки боевой системы."""

    min_damage: int = 1
    defense_reduction_factor: float = 0.5


@dataclass
class CharacterSettings:
    """Настройки персонажей."""

    base_max_hp: int = 50
    base_max_energy: int = 20
    hp_per_vitality: int = 5
    energy_per_intelligence: int = 3
    attack_per_strength: int = 2
    defense_per_agility: float = 1.5


@dataclass
class UISettings:
    """Настройки пользовательского интерфейса."""

    screen_width: int = 80
    screen_height: int = 24


@dataclass
class SystemSettings:
    """Системные настройки."""

    enable_debug_logging: bool = False
    log_file: str = "game.log"
    save_directory: str = "saves"
    autosave_interval: int = 300
    data_directory: str = "game/data"
    characters_data_directory: str = "game/data/characters"
    player_classes_directory: str = "game/data/characters/player_classes"


@dataclass
class GameConfig:
    """Основной класс конфигурации игры."""

    experience: ExperienceSettings = field(default_factory=ExperienceSettings)
    combat: CombatSettings = field(default_factory=CombatSettings)
    character: CharacterSettings = field(default_factory=CharacterSettings)
    ui: UISettings = field(default_factory=UISettings)
    system: SystemSettings = field(default_factory=SystemSettings)

    config_file: str = "config.json"

    def load_from_file(self, config_file: str = "") -> None:
        """
        Загрузить конфигурацию из файла.

        Args:
            config_file: Путь к файлу конфигурации. Если не указан, используется self.config_file.
        """
        file_path = config_file or self.config_file
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._update_from_dict(data)
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")

    def save_to_file(self, config_file: str = "") -> None:
        """
        Сохранить конфигурацию в файл.

        Args:
            config_file: Путь к файлу конфигурации. Если не указан, используется self.config_file.
        """
        file_path = config_file or self.config_file
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")

    def _to_dict(self) -> Dict[str, Any]:
        """Преобразовать конфигурацию в словарь."""
        return {
            'experience': {
                'formula_base': self.experience.formula_base,
                'formula_multiplier': self.experience.formula_multiplier,
            },
            'combat': {
                'min_damage': self.combat.min_damage,
                'defense_reduction_factor': self.combat.defense_reduction_factor,
            },
            'character': {
                'base_max_hp': self.character.base_max_hp,
                'base_max_energy': self.character.base_max_energy,
                'hp_per_vitality': self.character.hp_per_vitality,
                'energy_per_intelligence': self.character.energy_per_intelligence,
                'attack_per_strength': self.character.attack_per_strength,
                'defense_per_agility': self.character.defense_per_agility,
            },
            'ui': {
                'screen_width': self.ui.screen_width,
                'screen_height': self.ui.screen_height,
            },
            'system': {
                'enable_debug_logging': self.system.enable_debug_logging,
                'log_file': self.system.log_file,
                'save_directory': self.system.save_directory,
                'autosave_interval': self.system.autosave_interval,
                'data_directory': self.system.data_directory,
                'characters_data_directory': self.system.characters_data_directory,
                'player_classes_directory': self.system.player_classes_directory,
            }
        }

    def _update_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Обновить конфигурацию из словаря.

        Args:
            data: Словарь с данными конфигурации.
        """
        if 'experience' in data:
            for key, value in data['experience'].items():
                if hasattr(self.experience, key):
                    setattr(self.experience, key, value)

        if 'combat' in data:
            for key, value in data['combat'].items():
                if hasattr(self.combat, key):
                    setattr(self.combat, key, value)

        if 'character' in data:
            for key, value in data['character'].items():
                if hasattr(self.character, key):
                    setattr(self.character, key, value)

        if 'ui' in data:
            for key, value in data['ui'].items():
                if hasattr(self.ui, key):
                    setattr(self.ui, key, value)

        if 'system' in data:
            for key, value in data['system'].items():
                if hasattr(self.system, key):
                    setattr(self.system, key, value)


# Глобальный экземпляр конфигурации
game_config = GameConfig()


def get_config() -> GameConfig:
    """Получить глобальный экземпляр конфигурации."""
    return game_config
