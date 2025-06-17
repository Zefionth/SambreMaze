"""Конфигурация игры и управление настройками"""
import json

class Config:
    """Класс для конфигурации игры и управления настройками"""
    
    # Размеры экрана
    WIDTH, HEIGHT = 1000, 800
    
    # Цвета
    BLACK = (0, 0, 0)
    DARK = (15, 15, 25)
    WHITE = (255, 255, 255)
    RED = (255, 80, 80)
    GREEN = (100, 255, 100)
    BLUE = (100, 100, 255)
    GRAY = (100, 100, 100)
    LIGHT_GRAY = (200, 200, 200)
    
    # Настройки по умолчанию
    DEFAULT_SETTINGS = {
        'player_radius': 10,
        'player_speed': 3.5,
        'fog_radius': 150,
        'point_lifetime': 2500,
        'locator_cooldown': 25,
        'detector_cooldown': 500,
        'colors': {
            'background': DARK,
            'player': WHITE,
            'walls': WHITE,
            'exit': GREEN,
            'danger': RED,
            'locator': WHITE,
            'detector': RED
        }
    }
        
    @classmethod
    def load_settings(cls) -> dict:
        """Загружает настройки из JSON файла или возвращает настройки по умолчанию"""
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