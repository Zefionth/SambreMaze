"""Визуальное представление меню"""
import pygame
from src.config import Config

class MenuView:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont('Arial', 64)
        self.settings_font = pygame.font.SysFont('Arial', 48)
        self.ui_font = pygame.font.SysFont('Arial', 24)

    def draw(self, current_menu, main_buttons, settings_sliders, 
            color_pickers, settings_buttons, active_picker, color_sliders, colors):
        """Отрисовывает текущее состояние меню"""
        
        # Фон зависит от текущего меню
        if current_menu == "main":
            bg_color = colors['background']
            text_color = Config.WHITE
        else:
            bg_color = (240, 240, 230)  # Инвертированный DARK
            text_color = Config.BLACK

        self.screen.fill(bg_color)

        if current_menu == "main":
            # Заголовок главного меню
            title = self.title_font.render("Scanner Sombre", True, text_color)
            self.screen.blit(title, (Config.WIDTH//2 - title.get_width()//2, 100))

            # Кнопки
            for button in main_buttons:
                button.draw(self.screen)

        elif current_menu == "settings":
            # Заголовок настроек
            title = self.settings_font.render("Настройки", True, text_color)
            self.screen.blit(title, (Config.WIDTH//2 - title.get_width()//2, 50))

            # Элементы интерфейса
            for slider in settings_sliders:
                slider.draw(self.screen)

            for picker in color_pickers:
                picker.draw(self.screen)

            if active_picker:
                for slider in color_sliders:
                    slider.draw(self.screen)

            for button in settings_buttons:
                button.draw(self.screen)

        pygame.display.flip()