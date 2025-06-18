"""Визуальное представление меню"""
import pygame
from src.config import Config
from src.utils import center_text

class MenuView:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont('Arial', 64)
        self.settings_font = pygame.font.SysFont('Arial', 48)
        self.ui_font = pygame.font.SysFont('Arial', Config.UI_FONT_SIZE)

    def draw(self, current_menu, main_buttons, settings_sliders, 
            color_pickers, settings_buttons, active_picker, color_sliders, colors):
        """Отрисовывает текущее состояние меню"""
        self.screen.fill(colors['background'] if current_menu == "main" else (240, 240, 230))

        if current_menu == "main":
            # Заголовок главного меню
            title = self.title_font.render("Scanner Sombre", True, Config.WHITE)
            title_rect = title.get_rect(center=(Config.WIDTH//2, 100))
            self.screen.blit(title, title_rect)

            # Кнопки
            for button in main_buttons:
                button.draw(self.screen)

        elif current_menu == "settings":
            # Заголовок настроек
            title = self.settings_font.render("Настройки", True, Config.BLACK)
            title_rect = title.get_rect(center=(Config.WIDTH//2, 50))
            self.screen.blit(title, title_rect)

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