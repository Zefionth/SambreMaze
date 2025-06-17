"""Модель данных для меню"""
from src.config import Config
from src.view.ui_elements import Button, Slider, ColorPicker

class MenuModel:
    def __init__(self):
        self.settings = Config.load_settings()
        self.current_menu = "main"
        self.active_color_picker = None
        self.init_ui()

    def init_ui(self):
        center_x = Config.WIDTH // 2
        button_width, button_height = 200, 50
        
        # Кнопки главного меню
        self.main_menu_buttons = [
            Button(center_x - 100, 250, button_width, button_height, 
                 "Начать игру", Config.GREEN, (50, 200, 50)),
            Button(center_x - 100, 320, button_width, button_height,
                 "Настройки", Config.BLUE, (50, 50, 200)),
            Button(center_x - 100, 390, button_width, button_height,
                 "Выход", Config.RED, (200, 50, 50))
        ]

        # Слайдеры настроек
        self.settings_sliders = [
            Slider(150, 150, 200, 20, 5, 20, self.settings['player_radius'], "Размер игрока"),
            Slider(150, 200, 200, 20, 1, 10, self.settings['player_speed'], "Скорость игрока"),
            Slider(150, 250, 200, 20, 50, 300, self.settings['fog_radius'], "Радиус видимости"),
            Slider(150, 300, 200, 20, 500, 5000, self.settings['point_lifetime'], "Время жизни точек"),
            Slider(150, 350, 200, 20, 10, 100, self.settings['locator_cooldown'], "КД локатора"),
            Slider(150, 400, 200, 20, 100, 1000, self.settings['detector_cooldown'], "КД детектора"),
        ]

        # Цветовые пикеры
        self.color_pickers = [
            ColorPicker(450, 150, 50, 50, self.settings['colors']['background'], "Фон"),
            ColorPicker(450, 220, 50, 50, self.settings['colors']['player'], "Игрок"),
            ColorPicker(450, 290, 50, 50, self.settings['colors']['walls'], "Стены"),
            ColorPicker(450, 360, 50, 50, self.settings['colors']['exit'], "Выход"),
            ColorPicker(450, 430, 50, 50, self.settings['colors']['danger'], "Опасность"),
            ColorPicker(550, 150, 50, 50, self.settings['colors']['locator'], "Локатор"),
            ColorPicker(550, 220, 50, 50, self.settings['colors']['detector'], "Детектор")
        ]

        # RGB слайдеры для активного цветового пикера
        self.color_components = [
            Slider(650, 150, 200, 20, 0, 255, 0, "R"),
            Slider(650, 200, 200, 20, 0, 255, 0, "G"),
            Slider(650, 250, 200, 20, 0, 255, 0, "B")
        ]

        # Кнопки настроек
        self.settings_buttons = [
            Button(center_x - 100, 500, button_width, button_height,
                 "Сохранить", Config.GREEN, (50, 200, 50)),
            Button(center_x - 100, 570, button_width, button_height,
                 "Назад", Config.RED, (200, 50, 50))
        ]

        # Кнопка сброса
        self.settings_buttons = [
        Button(center_x - 210, 500, 100, 50,
              "Сброс", Config.GRAY, (150, 150, 150)),
        Button(center_x - 100, 500, 200, 50,
              "Сохранить", Config.GREEN, (50, 200, 50)),
        Button(center_x - 100, 570, 200, 50,
              "Назад", Config.RED, (200, 50, 50))
        ]

    def save_settings(self):
        """Сохраняет текущие настройки в файл"""
        self.settings = {
        'player_radius': int(self.settings_sliders[0].value),
        'player_speed': float(self.settings_sliders[1].value),
        'fog_radius': int(self.settings_sliders[2].value),
        'point_lifetime': int(self.settings_sliders[3].value),
        'locator_cooldown': int(self.settings_sliders[4].value),
        'detector_cooldown': int(self.settings_sliders[5].value),
        'colors': {
            'background': self.color_pickers[0].color,
            'player': self.color_pickers[1].color,
            'walls': self.color_pickers[2].color,
            'exit': self.color_pickers[3].color,
            'danger': self.color_pickers[4].color,
            'locator': self.color_pickers[5].color,
            'detector': self.color_pickers[6].color
        }
}
        Config.save_settings(self.settings)
    
    def reset_to_default(self):
        """Сбрасывает настройки к значениям по умолчанию"""
        default = Config.DEFAULT_SETTINGS
        
        # Сбрасываем слайдеры
        self.settings_sliders[0].value = default['player_radius']
        self.settings_sliders[1].value = default['player_speed']
        self.settings_sliders[2].value = default['fog_radius']
        self.settings_sliders[3].value = default['point_lifetime']
        self.settings_sliders[4].value = default['locator_cooldown']
        self.settings_sliders[5].value = default['detector_cooldown']
        
        # Обновляем слайдеры цветов
        if self.active_color_picker:
            self.update_color_sliders()
        
        # Сбрасываем слайдеры
        self.settings_sliders = [
        Slider(150, 150, 200, 20, 5, 20, self.settings['player_radius'], "Размер игрока"),
        Slider(150, 200, 200, 20, 1, 10, self.settings['player_speed'], "Скорость игрока"),
        Slider(150, 250, 200, 20, 50, 300, self.settings['fog_radius'], "Радиус видимости"),
        Slider(150, 300, 200, 20, 500, 5000, self.settings['point_lifetime'], "Время жизни точек"),
        Slider(150, 350, 200, 20, 10, 100, self.settings['locator_cooldown'], "КД локатора"),
        Slider(150, 400, 200, 20, 100, 1000, self.settings['detector_cooldown'], "КД детектора")
        ]
            
        # Сбрасываем цвета
        self.color_pickers = [
            ColorPicker(450, 150, 50, 50, default['colors']['background'], "Фон"),
            ColorPicker(450, 220, 50, 50, default['colors']['player'], "Игрок"),
            ColorPicker(450, 290, 50, 50, default['colors']['walls'], "Стены"),
            ColorPicker(450, 360, 50, 50, default['colors']['exit'], "Выход"),
            ColorPicker(450, 430, 50, 50, default['colors']['danger'], "Опасность"),
            ColorPicker(550, 150, 50, 50, default['colors']['locator'], "Локатор"),
            ColorPicker(550, 220, 50, 50, default['colors']['detector'], "Детектор")
        ]
        
        # Сбрасываем RGB слайдеры
        self.color_components = [
            Slider(650, 150, 200, 20, 0, 255, 0, "R"),
            Slider(650, 200, 200, 20, 0, 255, 0, "G"),
            Slider(650, 250, 200, 20, 0, 255, 0, "B")
        ]
        
        self.active_color_picker = None
        
        # Применяем изменения
        self.apply_settings_immediately()

    def update_color_sliders(self):
        """Обновляет слайдеры RGB при выборе цветового пикера"""
        if self.active_color_picker:
            for i in range(3):
                self.color_components[i].value = self.active_color_picker.color[i]
    
    def apply_settings_immediately(self):
        """Применяет настройки с проверкой всех ключей"""
        temp_settings = {
            'player_radius': int(self.settings_sliders[0].value),
            'player_speed': float(self.settings_sliders[1].value),
            'fog_radius': int(self.settings_sliders[2].value),
            'point_lifetime': int(self.settings_sliders[3].value),
            'locator_cooldown': int(self.settings_sliders[4].value),
            'detector_cooldown': int(self.settings_sliders[5].value),
            'colors': {
                'background': self.color_pickers[0].color,
                'player': self.color_pickers[1].color,
                'walls': self.color_pickers[2].color,
                'exit': self.color_pickers[3].color,
                'danger': self.color_pickers[4].color,
                'locator': self.color_pickers[5].color,
                'detector': self.color_pickers[6].color
            }
        }
        if hasattr(self, 'game'):
            self.game.apply_settings(temp_settings)