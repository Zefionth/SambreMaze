"""Класс меню игры"""
import pygame
from src.config import Config
from .buttons import Button
from .sliders import Slider
from .color_picker import ColorPicker

class Menu:
    def __init__(self, game):
        self.game = game
        self.current_menu = "main"
        self.settings = Config.load_settings()
        self.init_ui()
    
    def init_ui(self) -> None:
        center_x = Config.WIDTH // 2
        button_width, button_height = 200, 50
        
        self.main_menu_buttons = [
            Button(center_x - 100, 250, button_width, button_height, 
                  "Начать игру", Config.GREEN, (50, 200, 50)),
            Button(center_x - 100, 320, button_width, button_height, 
                  "Настройки", Config.BLUE, (50, 50, 200)),
            Button(center_x - 100, 390, button_width, button_height, 
                  "Выход", Config.RED, (200, 50, 50))
        ]
        
        self.settings_sliders = [
            Slider(150, 150, 200, 20, 5, 20, self.settings['player_radius'], "Размер игрока"),
            Slider(150, 200, 200, 20, 1, 10, self.settings['player_speed'], "Скорость игрока"),
            Slider(150, 250, 200, 20, 50, 300, self.settings['fog_radius'], "Радиус видимости"),
            Slider(150, 300, 200, 20, 500, 5000, self.settings['point_lifetime'], "Время жизни точек"),
            Slider(150, 350, 200, 20, 10, 100, self.settings['white_scan_cooldown'], "КД белого скана"),
            Slider(150, 400, 200, 20, 100, 1000, self.settings['red_scan_cooldown'], "КД красного скана")
        ]
        
        self.color_pickers = [
            ColorPicker(450, 150, 50, 50, self.settings['colors']['background'], "Фон"),
            ColorPicker(450, 220, 50, 50, self.settings['colors']['player'], "Игрок"),
            ColorPicker(450, 290, 50, 50, self.settings['colors']['walls'], "Стены"),
            ColorPicker(450, 360, 50, 50, self.settings['colors']['exit'], "Выход"),
            ColorPicker(450, 430, 50, 50, self.settings['colors']['danger'], "Опасность"),
            ColorPicker(550, 150, 50, 50, self.settings['colors']['scan'], "Скан"),
            ColorPicker(550, 220, 50, 50, self.settings['colors']['red_scan'], "Красный скан")
        ]
        
        self.settings_buttons = [
            Button(center_x - 100, 500, button_width, button_height, 
                  "Сохранить", Config.GREEN, (50, 200, 50)),
            Button(center_x - 100, 570, button_width, button_height, 
                  "Назад", Config.RED, (200, 50, 50))
        ]
        
        self.color_components = [
            Slider(650, 150, 200, 20, 0, 255, self.settings['colors']['background'][0], "R"),
            Slider(650, 200, 200, 20, 0, 255, self.settings['colors']['background'][1], "G"),
            Slider(650, 250, 200, 20, 0, 255, self.settings['colors']['background'][2], "B")
        ]
        
        self.active_color_picker = None
    
    def handle_events(self) -> bool:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if self.current_menu == "main":
                for button in self.main_menu_buttons:
                    button.check_hover(mouse_pos)
                    if button.is_clicked(mouse_pos, mouse_click):
                        if button.text == "Начать игру":
                            self.game.start_game()
                            return True
                        elif button.text == "Настройки":
                            self.current_menu = "settings"
                        elif button.text == "Выход":
                            return False
            
            elif self.current_menu == "settings":
                for slider in self.settings_sliders:
                    slider.handle_event(event)
                
                for picker in self.color_pickers:
                    if picker.handle_event(event):
                        self.active_color_picker = picker
                        self.color_components[0].value = picker.color[0]
                        self.color_components[1].value = picker.color[1]
                        self.color_components[2].value = picker.color[2]
                
                if self.active_color_picker:
                    for i, slider in enumerate(self.color_components):
                        if slider.handle_event(event):
                            self.active_color_picker.color[i] = int(slider.value)
                
                for button in self.settings_buttons:
                    button.check_hover(mouse_pos)
                    if button.is_clicked(mouse_pos, mouse_click):
                        if button.text == "Сохранить":
                            self.save_settings()
                        elif button.text == "Назад":
                            self.current_menu = "main"
        
        return True
    
    def save_settings(self) -> None:
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
        self.game.apply_settings(self.settings)
    
    def draw(self, surface: pygame.Surface) -> None:
        # Определяем цвет фона
        if self.current_menu == "main":
            bg_color = self.settings['colors']['background']
            text_color = Config.WHITE
        else:  # settings
            # Инвертируем основной цвет фона (DARK = (15, 15, 25) -> (240, 240, 230)
            bg_color = (240, 240, 230)
            text_color = Config.BLACK
        
        surface.fill(bg_color)
        
        if self.current_menu == "main":
            # Заголовок главного меню
            title_font = pygame.font.SysFont('Arial', 64)
            title = title_font.render("Scanner Sombre", True, text_color)
            surface.blit(title, (Config.WIDTH//2 - title.get_width()//2, 100))
            
            # Кнопки
            for button in self.main_menu_buttons:
                button.draw(surface)
        
        elif self.current_menu == "settings":
            # Заголовок настроек
            title_font = pygame.font.SysFont('Arial', 48)
            title = title_font.render("Настройки", True, text_color)
            surface.blit(title, (Config.WIDTH//2 - title.get_width()//2, 50))
            
            # Остальные элементы
            for slider in self.settings_sliders:
                slider.draw(surface)
            
            for picker in self.color_pickers:
                picker.draw(surface)
            
            if self.active_color_picker:
                for slider in self.color_components:
                    slider.draw(surface)
            
            for button in self.settings_buttons:
                button.draw(surface)
        
        pygame.display.flip()