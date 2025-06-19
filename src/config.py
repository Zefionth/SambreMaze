"""Конфигурация игры и управление настройками"""
import json
import pygame

class Config:
    """Основной класс для хранения конфигурации игры"""
    
    # Размеры экрана
    WIDTH, HEIGHT = 1000, 800
    
    # Размеры игровых элементов
    CELL_SIZE = 30
    START_ZONE_SIZE = 1
    DANGER_ZONE_RATIO = 0.3
    
    # Игровые константы
    DIAGONAL_FACTOR = 0.7071  # 1/sqrt(2)
    MAX_GLOW = 10
    GLOW_INCREASE = 1
    GLOW_DECAY_RATE = 5
    PULSE_SPEED = 0.1
    
    # Настройки частиц
    PARTICLE_SIZE = 2
    PARTICLE_LIFETIME = 0.4
    PARTICLE_SPEED = 0.2
    PARTICLE_SPEED_FACTOR = 60
    GAMEOVER_PARTICLE_SIZE = 15
    GAMEOVER_PARTICLE_LIFETIME = 2.0
    
    # Настройки локатора
    LOCATOR_SCAN_LENGTH = 200
    LOCATOR_SCAN_STEP = 1
    LOCATOR_ANGLE_VARIATION = 0.02
    LOCATOR_HIT_VARIATION = 2
    LOCATOR_PULSE_FACTOR = 1.5
    LOCATOR_BASE_RADIUS = 3
    
    # Настройки детектора
    DETECTOR_SCAN_LENGTH = 200
    DETECTOR_SCAN_STEP = 3
    DETECTOR_ANGLE_MIN = -45
    DETECTOR_ANGLE_MAX = 46
    DETECTOR_ANGLE_STEP = 2
    DETECTOR_WAVE_DURATION = 500
    DETECTOR_PULSE_FACTOR = 2.0
    DETECTOR_BASE_RADIUS = 1
    DETECTOR_POINT_SIZE = 1
    DETECTOR_ALPHA = 150
    DETECTOR_LINE_ALPHA = 20
    DETECTOR_LINE_WIDTH = 1

    # Настройки отображения игры
    PATH_LINE_WIDTH = 3
    FOG_ALPHA = 200
    EXIT_PULSE_SIZE = 3
    EXIT_GLOW_ALPHA = 50
    
    # Настройки игрока
    PLAYER_DIRECTION_SIZE = 1.5
    PLAYER_WING_ANGLE = 2.3
    PLAYER_WING_SIZE = 0.8
    PLAYER_GLOW_MIN = 180
    PLAYER_GLOW_FACTOR = 7.5
    
    # Настройки UI
    FONT_NAME = 'Arial'
    TITLE_FONT_SIZE = 64
    SETTINGS_FONT_SIZE = 48
    UI_FONT_SIZE = 24
    INFO_FONT_SIZE = 20
    UI_BORDER_WIDTH = 2
    BUTTON_WIDTH = 200
    BUTTON_HEIGHT = 50
    SLIDER_KNOB_WIDTH = 20
    SLIDER_TEXT_OFFSET = 25
    
    # Цвета
    BLACK = (0, 0, 0)
    DARK = (15, 15, 25)
    WHITE = (255, 255, 255)
    RED = (255, 80, 80)
    GREEN = (100, 255, 100)
    BLUE = (100, 100, 255)
    GRAY = (100, 100, 100)
    LIGHT_GRAY = (200, 200, 200)
    
    # Цвета кнопок при наведении
    BUTTON_HOVER_GREEN = (50, 200, 50)
    BUTTON_HOVER_BLUE = (50, 50, 200)
    BUTTON_HOVER_RED = (200, 50, 50)
    BUTTON_HOVER_GRAY = (150, 150, 150)

    # Громкость звуков
    SOUND_VOLUMES = {
        'click': 0.7,
        'locator': 0.5,
        'detector': 0.6,
        'win': 0.8,
        'lose': 0.8
    }
    
    # Настройки по умолчанию
    DEFAULT_SETTINGS = {
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
    def load_settings(cls) -> dict:
        """Загружает настройки из JSON файла"""
        try:
            with open('settings.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return cls.DEFAULT_SETTINGS
    
    @classmethod
    def save_settings(cls, settings: dict) -> None:
        """Сохраняет текущие настройки в JSON файл"""
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)