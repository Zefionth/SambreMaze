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
            Slider(150, 350, 200, 20, 10, 100, self.settings['white_scan_cooldown'], "КД белого скана"),
            Slider(150, 400, 200, 20, 100, 1000, self.settings['red_scan_cooldown'], "КД красного скана")
        ]

        # Цветовые пикеры
        self.color_pickers = [
            ColorPicker(450, 150, 50, 50, self.settings['colors']['background'], "Фон"),
            ColorPicker(450, 220, 50, 50, self.settings['colors']['player'], "Игрок"),
            ColorPicker(450, 290, 50, 50, self.settings['colors']['walls'], "Стены"),
            ColorPicker(450, 360, 50, 50, self.settings['colors']['exit'], "Выход"),
            ColorPicker(450, 430, 50, 50, self.settings['colors']['danger'], "Опасность"),
            ColorPicker(550, 150, 50, 50, self.settings['colors']['scan'], "Скан"),
            ColorPicker(550, 220, 50, 50, self.settings['colors']['red_scan'], "Красный скан")
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

    def save_settings(self):
        """Сохраняет текущие настройки в файл"""
        self.settings = {
            'player_radius': int(self.settings_sliders[0].value),
            'player_speed': float(self.settings_sliders[1].value),
            'fog_radius': int(self.settings_sliders[2].value),
            'point_lifetime': int(self.settings_sliders[3].value),
            'white_scan_cooldown': int(self.settings_sliders[4].value),
            'red_scan_cooldown': int(self.settings_sliders[5].value),
            'colors': {
                'background': self.color_pickers[0].color,
                'player': self.color_pickers[1].color,
                'walls': self.color_pickers[2].color,
                'exit': self.color_pickers[3].color,
                'danger': self.color_pickers[4].color,
                'scan': self.color_pickers[5].color,
                'red_scan': self.color_pickers[6].color
            }
        }
        Config.save_settings(self.settings)