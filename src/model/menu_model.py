"""Модель данных для меню.

Этот модуль содержит класс MenuModel, который управляет данными меню,
включая настройки игры, состояние интерфейса и элементы управления.
"""

from src.config import Config
from src.view.ui_elements import Button, Slider, ColorPicker
from typing import Any, Optional


class MenuModel:
    """Модель данных для меню игры.
    
    Отвечает за:
    - Хранение текущих настроек игры
    - Управление состоянием меню (главное/настройки)
    - Инициализацию и обновление элементов интерфейса
    - Сохранение и сброс настроек
    - Применение настроек к игровому контроллеру
    
    Attributes:
        settings (dict): Текущие настройки игры
        current_menu (str): Текущее активное меню ('main' или 'settings')
        active_color_picker (Optional[ColorPicker]): Активный цветовой пикер
        main_menu_buttons (List[Button]): Кнопки главного меню
        settings_sliders (List[Slider]): Слайдеры настроек
        color_pickers (List[ColorPicker]): Цветовые пикеры
        color_components (List[Slider]): Слайдеры RGB компонентов
        settings_buttons (List[Button]): Кнопки меню настроек
        game (Optional[GameController]): Ссылка на игровой контроллер
    """
    
    def __init__(self) -> None:
        """Инициализирует модель меню, загружая настройки и создавая UI."""
        self.settings = Config.load_settings()
        self.current_menu = "main"
        self.active_color_picker: Optional[ColorPicker] = None
        self.game: Optional[Any] = None
        self.init_ui()

    def init_ui(self) -> None:
        """Инициализирует элементы пользовательского интерфейса."""
        center_x = Config.WIDTH // 2
        button_width, button_height = Config.BUTTON_WIDTH, Config.BUTTON_HEIGHT
        
        # Кнопки главного меню
        self.main_menu_buttons = [
            Button(
                center_x - 100, 250, button_width, button_height,
                "Начать игру", Config.GREEN, Config.BUTTON_HOVER_GREEN
            ),
            Button(
                center_x - 100, 320, button_width, button_height,
                "Настройки", Config.BLUE, Config.BUTTON_HOVER_BLUE
            ),
            Button(
                center_x - 100, 390, button_width, button_height,
                "Выход", Config.RED, Config.BUTTON_HOVER_RED
            )
        ]

        # Слайдеры настроек
        self.settings_sliders = [
            Slider(150, 150, 200, 20, 5, 20, 
                   self.settings['player_radius'], "Размер игрока"),
            Slider(150, 200, 200, 20, 1, 10, 
                   self.settings['player_speed'], "Скорость игрока"),
            Slider(150, 250, 200, 20, 50, 300, 
                   self.settings['fog_radius'], "Радиус видимости"),
            Slider(150, 300, 200, 20, 500, 5000, 
                   self.settings['point_lifetime'], "Время жизни точек"),
            Slider(150, 350, 200, 20, 10, 100, 
                   self.settings['locator_cooldown'], "КД локатора"),
            Slider(150, 400, 200, 20, 100, 1000, 
                   self.settings['detector_cooldown'], "КД детектора"),
        ]

        # Цветовые пикеры
        self.color_pickers = [
            ColorPicker(450, 150, 50, 50, 
                        self.settings['colors']['player'], "Игрок"),
            ColorPicker(450, 220, 50, 50, 
                        self.settings['colors']['exit'], "Выход"),
            ColorPicker(450, 290, 50, 50, 
                        self.settings['colors']['locator'], "Локатор"),
            ColorPicker(450, 360, 50, 50, 
                        self.settings['colors']['detector'], "Детектор")
        ]

        # RGB слайдеры для активного цветового пикера
        self.color_components = [
            Slider(650, 150, 200, 20, 0, 255, 0, "R"),
            Slider(650, 200, 200, 20, 0, 255, 0, "G"),
            Slider(650, 250, 200, 20, 0, 255, 0, "B")
        ]

        # Кнопки настроек
        self.settings_buttons = [
            Button(
                center_x - 210, 500, 100, 50,
                "Сброс", Config.GRAY, Config.BUTTON_HOVER_GRAY
            ),
            Button(
                center_x - 100, 500, 200, 50,
                "Сохранить", Config.GREEN, Config.BUTTON_HOVER_GREEN
            ),
            Button(
                center_x - 100, 570, 200, 50,
                "Назад", Config.RED, Config.BUTTON_HOVER_RED
            )
        ]

    def save_settings(self) -> None:
        """Сохраняет текущие настройки в файл и обновляет модель."""
        self.settings = {
            'player_radius': int(self.settings_sliders[0].value),
            'player_speed': float(self.settings_sliders[1].value),
            'fog_radius': int(self.settings_sliders[2].value),
            'point_lifetime': int(self.settings_sliders[3].value),
            'locator_cooldown': int(self.settings_sliders[4].value),
            'detector_cooldown': int(self.settings_sliders[5].value),
            'colors': {
                'player': self.color_pickers[0].color,
                'exit': self.color_pickers[1].color,
                'locator': self.color_pickers[2].color,
                'detector': self.color_pickers[3].color
            }
        }
        Config.save_settings(self.settings)
    
    def reset_to_default(self) -> None:
        """Сбрасывает настройки к значениям по умолчанию."""
        default = Config.DEFAULT_SETTINGS
        
        # Обновляем текущие настройки
        self.settings = default.copy()
        
        # Сбрасываем слайдеры основных настроек
        slider_keys = [
            'player_radius',
            'player_speed',
            'fog_radius',
            'point_lifetime',
            'locator_cooldown',
            'detector_cooldown'
        ]
        for i, key in enumerate(slider_keys):
            self.settings_sliders[i].value = default[key]
            self.settings_sliders[i].update_knob()
        
        # Сбрасываем цветовые пикеры
        color_keys = ['player', 'exit', 'locator', 'detector']
        for i, key in enumerate(color_keys):
            self.color_pickers[i].color = list(default['colors'][key])
        
        # Обновляем слайдеры цветов, если активен пикер
        if self.active_color_picker:
            self.update_color_sliders()
        
        # Применяем изменения немедленно
        self.apply_settings_immediately()

    def update_color_sliders(self) -> None:
        """Обновляет слайдеры RGB при выборе цветового пикера."""
        if self.active_color_picker:
            for i in range(3):
                self.color_components[i].value = self.active_color_picker.color[i]
                self.color_components[i].update_knob()
    
    def apply_settings_immediately(self) -> None:
        """Применяет текущие настройки к игровому контроллеру."""
        temp_settings = {
            'player_radius': int(self.settings_sliders[0].value),
            'player_speed': float(self.settings_sliders[1].value),
            'fog_radius': int(self.settings_sliders[2].value),
            'point_lifetime': int(self.settings_sliders[3].value),
            'locator_cooldown': int(self.settings_sliders[4].value),
            'detector_cooldown': int(self.settings_sliders[5].value),
            'colors': {
                'player': self.color_pickers[0].color,
                'exit': self.color_pickers[1].color,
                'locator': self.color_pickers[2].color,
                'detector': self.color_pickers[3].color
            }
        }
        if hasattr(self, 'game') and self.game:
            self.game.apply_settings(temp_settings)