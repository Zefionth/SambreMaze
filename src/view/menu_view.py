"""Визуальное представление меню"""
import pygame
from src.config import Config
from src.utils import center_text

class MenuView:
    def __init__(self, screen):
        self.screen = screen
        self.title_font = pygame.font.SysFont(Config.FONT_NAME, Config.TITLE_FONT_SIZE)
        self.settings_font = pygame.font.SysFont(Config.FONT_NAME, Config.SETTINGS_FONT_SIZE)
        self.ui_font = pygame.font.SysFont(Config.FONT_NAME, Config.UI_FONT_SIZE)
        self.info_font = pygame.font.SysFont(Config.FONT_NAME, Config.INFO_FONT_SIZE)

    def draw(self, current_menu, main_buttons, settings_sliders, 
            color_pickers, settings_buttons, active_picker, color_sliders, colors):
        """Отрисовывает текущее состояние меню"""
        # Очищаем экран перед отрисовкой
        if current_menu == "main":
            self.screen.fill(Config.DARK)  # Темный фон для главного меню
            
            # Заголовок главного меню
            title = self.title_font.render("Scanner Sombre", True, Config.WHITE)
            title_rect = title.get_rect(center=(Config.WIDTH//2, 100))
            self.screen.blit(title, title_rect)

            # Кнопки
            for button in main_buttons:
                button.draw(self.screen)
            
            # Объяснение локатора (слева)
            self._draw_tool_info(
                x=50,
                y=500,
                title="Локатор (ЛКМ)",
                description=[
                    "• Поток едининых импульсов",
                    "в направлении курсора",
                    "• Показывает ближайшую стену",
                    "• Работает при зажатии",
                    "• Используйте для навигации"
                ],
                color=Config.WHITE
            )
            
            # Объяснение детектора (справа)
            self._draw_tool_info(
                x=Config.WIDTH - 450,
                y=500,
                title="Детектор (ПКМ)",
                description=[
                    "• Широкий импульс в направлении курсора",
                    "• Показывает опасные зоны",
                    "• Работает при единичном нажатии",
                    "• Используйте для обнаружения ловушек"
                ],
                color=Config.RED
            )

        elif current_menu == "settings":
            # Очищаем экран светлым фоном для меню настроек
            self.screen.fill((240, 240, 230))
            
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
    
    def _draw_tool_info(self, x, y, title, description, color):
        """Отрисовывает информацию о инструменте"""
        title_surface = self.info_font.render(title, True, color)
        self.screen.blit(title_surface, (x, y))
        
        for i, line in enumerate(description):
            text_surface = self.info_font.render(line, True, Config.WHITE)
            self.screen.blit(text_surface, (x, y + 40 + i * 30))