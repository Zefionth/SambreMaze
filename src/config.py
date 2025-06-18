"""Конфигурация игры и управление настройками.

Содержит настройки по умолчанию, методы для загрузки/сохранения настроек,
а также основные константы, используемые в игре (размеры экрана, цвета и т.д.).
"""
import json

class Config:
    """Основной класс для хранения конфигурации игры.
    
    Атрибуты:
        WIDTH (int): Ширина игрового окна в пикселях
        HEIGHT (int): Высота игрового окна в пикселях
        DEFAULT_SETTINGS (dict): Настройки по умолчанию
    """
    
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
        """Загружает настройки из JSON файла.
        
        Если файл не найден или поврежден, возвращает настройки по умолчанию.
        
        Returns:
            dict: Загруженные настройки или DEFAULT_SETTINGS
        """
        try:
            with open('settings.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return cls.DEFAULT_SETTINGS
    
    @classmethod
    def save_settings(cls, settings: dict) -> None:
        """Сохраняет текущие настройки в JSON файл.
        
        Args:
            settings (dict): Словарь с настройками для сохранения
        """
        with open('settings.json', 'w') as f:
            json.dump(settings, f, indent=4)