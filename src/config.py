"""Конфигурация игры и управление настройками.

Этот модуль содержит класс Config, который хранит все константы игры,
настройки по умолчанию и методы для работы с файлом настроек.
"""

import json
import pygame
from typing import Dict, Any, Tuple


class Config:
    """Основной класс для хранения конфигурации игры.
    
    Содержит все константы игры, настройки по умолчанию и методы
    для загрузки/сохранения настроек из/в файл.
    
    Attributes:
        WIDTH (int): Ширина игрового окна
        HEIGHT (int): Высота игрового окна
        CELL_SIZE (int): Размер ячейки лабиринта
        START_ZONE_SIZE (int): Размер стартовой зоны
        DANGER_ZONE_RATIO (float): Процент опасных зон
        DIAGONAL_FACTOR (float): Коэффициент скорости при диагональном движении
        ... (все остальные атрибуты)
    """
    
    # Размеры экрана
    WIDTH: int = 1000
    HEIGHT: int = 800
    
    # Размеры игровых элементов
    CELL_SIZE: int = 30
    START_ZONE_SIZE: int = 1
    DANGER_ZONE_RATIO: float = 0.3
    
    # Игровые константы
    DIAGONAL_FACTOR: float = 0.7071  # 1/sqrt(2)
    MAX_GLOW: int = 10
    GLOW_INCREASE: int = 1
    GLOW_DECAY_RATE: int = 5
    PULSE_SPEED: float = 0.1
    
    # Настройки частиц
    PARTICLE_SIZE: int = 2
    PARTICLE_LIFETIME: float = 0.4
    PARTICLE_SPEED: float = 0.2
    PARTICLE_SPEED_FACTOR: int = 60
    GAMEOVER_PARTICLE_SIZE: int = 15
    GAMEOVER_PARTICLE_LIFETIME: float = 2.0
    
    # Настройки локатора
    LOCATOR_SCAN_LENGTH: int = 200
    LOCATOR_SCAN_STEP: int = 1
    LOCATOR_ANGLE_VARIATION: float = 0.02
    LOCATOR_HIT_VARIATION: int = 2
    LOCATOR_PULSE_FACTOR: float = 1.5
    LOCATOR_BASE_RADIUS: int = 3
    
    # Настройки детектора
    DETECTOR_SCAN_LENGTH: int = 200
    DETECTOR_SCAN_STEP: int = 3
    DETECTOR_ANGLE_MIN: int = -45
    DETECTOR_ANGLE_MAX: int = 46
    DETECTOR_ANGLE_STEP: int = 2
    DETECTOR_WAVE_DURATION: int = 500
    DETECTOR_PULSE_FACTOR: float = 2.0
    DETECTOR_BASE_RADIUS: int = 1
    DETECTOR_POINT_SIZE: int = 1
    DETECTOR_ALPHA: int = 150
    DETECTOR_LINE_ALPHA: int = 20
    DETECTOR_LINE_WIDTH: int = 1

    # Настройки отображения игры
    PATH_LINE_WIDTH: int = 3
    FOG_ALPHA: int = 200
    EXIT_PULSE_SIZE: int = 3
    EXIT_GLOW_ALPHA: int = 50
    
    # Настройки игрока
    PLAYER_DIRECTION_SIZE: float = 1.5
    PLAYER_WING_ANGLE: float = 2.3
    PLAYER_WING_SIZE: float = 0.8
    PLAYER_GLOW_MIN: int = 180
    PLAYER_GLOW_FACTOR: float = 7.5
    
    # Настройки UI
    FONT_NAME: str = 'Arial'
    TITLE_FONT_SIZE: int = 64
    SETTINGS_FONT_SIZE: int = 48
    UI_FONT_SIZE: int = 24
    INFO_FONT_SIZE: int = 20
    UI_BORDER_WIDTH: int = 2
    BUTTON_WIDTH: int = 200
    BUTTON_HEIGHT: int = 50
    SLIDER_KNOB_WIDTH: int = 20
    SLIDER_TEXT_OFFSET: int = 25
    
    # Цвета
    BLACK: Tuple[int, int, int] = (0, 0, 0)
    DARK: Tuple[int, int, int] = (15, 15, 25)
    WHITE: Tuple[int, int, int] = (255, 255, 255)
    RED: Tuple[int, int, int] = (255, 80, 80)
    GREEN: Tuple[int, int, int] = (100, 255, 100)
    BLUE: Tuple[int, int, int] = (100, 100, 255)
    GRAY: Tuple[int, int, int] = (100, 100, 100)
    LIGHT_GRAY: Tuple[int, int, int] = (200, 200, 200)
    
    # Цвета кнопок при наведении
    BUTTON_HOVER_GREEN: Tuple[int, int, int] = (50, 200, 50)
    BUTTON_HOVER_BLUE: Tuple[int, int, int] = (50, 50, 200)
    BUTTON_HOVER_RED: Tuple[int, int, int] = (200, 50, 50)
    BUTTON_HOVER_GRAY: Tuple[int, int, int] = (150, 150, 150)

    # Громкость звуков
    SOUND_VOLUMES: Dict[str, float] = {
        'click': 0.7,
        'locator': 0.5,
        'detector': 0.6,
        'win': 0.8,
        'lose': 0.8
    }
    
    # Настройки по умолчанию
    DEFAULT_SETTINGS: Dict[str, Any] = {
        'player_radius': 10,
        'player_speed': 3.5,
        'fog_radius': 150,
        'point_lifetime': 2500,
        'locator_cooldown': 25,
        'detector_cooldown': 500,
        'colors': {
            'player': WHITE,
            'exit': GREEN,
            'locator': WHITE,
            'detector': RED
        }
    }
    
    @classmethod
    def load_settings(cls) -> Dict[str, Any]:
        """Загружает настройки из JSON файла.
        
        Returns:
            Dict[str, Any]: Загруженные настройки или настройки по умолчанию
        """
        try:
            with open('settings.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return cls.DEFAULT_SETTINGS
    
    @classmethod
    def save_settings(cls, settings: Dict[str, Any]) -> None:
        """Сохраняет текущие настройки в JSON файл.
        
        Args:
            settings: Словарь настроек для сохранения
        """
        with open('settings.json', 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)