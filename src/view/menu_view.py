"""Визуальное представление меню.

Этот модуль содержит класс MenuView, который отвечает за отрисовку
всех элементов меню, включая главное меню и меню настроек.
"""

import pygame
from src.config import Config
from src.utils import center_text
from src.view.ui_elements import Button, Slider, ColorPicker
from typing import List, Tuple, Dict, Any, Optional


class MenuView:
    """Класс для визуального представления игрового меню.
    
    Отвечает за:
    - Отрисовку главного меню с кнопками и описанием
    - Отрисовку меню настроек с элементами управления
    - Визуализацию информации об инструментах игры
    
    Attributes:
        screen (pygame.Surface): Основная поверхность для отрисовки
        title_font (pygame.font.Font): Шрифт для заголовков
        settings_font (pygame.font.Font): Шрифт для заголовка настроек
        ui_font (pygame.font.Font): Шрифт для элементов интерфейса
        info_font (pygame.font.Font): Шрифт для информационных текстов
    """
    
    def __init__(self, screen: pygame.Surface) -> None:
        """Инициализирует представление меню.
        
        Args:
            screen: Основная поверхность Pygame для отрисовки
        """
        self.screen = screen
        self.title_font = pygame.font.SysFont(
            Config.FONT_NAME, 
            Config.TITLE_FONT_SIZE
        )
        self.settings_font = pygame.font.SysFont(
            Config.FONT_NAME, 
            Config.SETTINGS_FONT_SIZE
        )
        self.ui_font = pygame.font.SysFont(
            Config.FONT_NAME, 
            Config.UI_FONT_SIZE
        )
        self.info_font = pygame.font.SysFont(
            Config.FONT_NAME, 
            Config.INFO_FONT_SIZE
        )

    def draw(
        self, 
        current_menu: str, 
        main_buttons: List[Button], 
        settings_sliders: List[Slider], 
        color_pickers: List[ColorPicker], 
        settings_buttons: List[Button], 
        active_picker: Optional[ColorPicker], 
        color_sliders: List[Slider], 
        colors: Dict[str, Tuple[int, int, int]]
    ) -> None:
        """Отрисовывает текущее состояние меню.
        
        Args:
            current_menu: Текущее активное меню ('main' или 'settings')
            main_buttons: Кнопки главного меню
            settings_sliders: Слайдеры настроек
            color_pickers: Цветовые пикеры
            settings_buttons: Кнопки меню настроек
            active_picker: Активный цветовой пикер (если есть)
            color_sliders: Слайдеры RGB компонентов
            colors: Словарь цветов (не используется)
        """
        if current_menu == "main":
            self._draw_main_menu(main_buttons)
        elif current_menu == "settings":
            self._draw_settings_menu(
                settings_sliders, 
                color_pickers, 
                settings_buttons, 
                active_picker, 
                color_sliders
            )
            
        pygame.display.flip()
    
    def _draw_main_menu(self, main_buttons: List[Button]) -> None:
        """Отрисовывает главное меню.
        
        Args:
            main_buttons: Список кнопок главного меню
        """
        # Устанавливаем темный фон
        self.screen.fill(Config.DARK)
        
        # Отрисовываем заголовок
        title = self.title_font.render("Scanner Sombre", True, Config.WHITE)
        title_rect = title.get_rect(center=(Config.WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        # Отрисовываем кнопки
        for button in main_buttons:
            button.draw(self.screen)
        
        # Отрисовываем информацию о локаторе (слева)
        self._draw_tool_info(
            x=50,
            y=500,
            title="Локатор (ЛКМ)",
            description=[
                "• Поток единичных импульсов",
                "в направлении курсора",
                "• Показывает ближайшую стену",
                "• Работает при зажатии",
                "• Используйте для навигации"
            ],
            color=Config.WHITE
        )
        
        # Отрисовываем информацию о детекторе (справа)
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

    def _draw_settings_menu(
        self, 
        settings_sliders: List[Slider], 
        color_pickers: List[ColorPicker], 
        settings_buttons: List[Button], 
        active_picker: Optional[ColorPicker], 
        color_sliders: List[Slider]
    ) -> None:
        """Отрисовывает меню настроек.
        
        Args:
            settings_sliders: Слайдеры настроек
            color_pickers: Цветовые пикеры
            settings_buttons: Кнопки меню настроек
            active_picker: Активный цветовой пикер
            color_sliders: Слайдеры RGB компонентов
        """
        # Устанавливаем светлый фон
        self.screen.fill((240, 240, 230))
        
        # Отрисовываем заголовок настроек
        title = self.settings_font.render("Настройки", True, Config.BLACK)
        title_rect = title.get_rect(center=(Config.WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # Отрисовываем элементы интерфейса
        for slider in settings_sliders:
            slider.draw(self.screen)

        for picker in color_pickers:
            picker.draw(self.screen)

        # Если есть активный пикер, отрисовываем RGB слайдеры
        if active_picker:
            for slider in color_sliders:
                slider.draw(self.screen)

        for button in settings_buttons:
            button.draw(self.screen)
    
    def _draw_tool_info(
        self, 
        x: int, 
        y: int, 
        title: str, 
        description: List[str], 
        color: Tuple[int, int, int]
    ) -> None:
        """Отрисовывает информацию об игровом инструменте.
        
        Args:
            x: X-координата начала блока
            y: Y-координата начала блока
            title: Заголовок инструмента
            description: Список строк описания
            color: Цвет заголовка (RGB)
        """
        # Отрисовываем заголовок
        title_surface = self.info_font.render(title, True, color)
        self.screen.blit(title_surface, (x, y))
        
        # Отрисовываем строки описания
        for i, line in enumerate(description):
            text_surface = self.info_font.render(line, True, Config.WHITE)
            self.screen.blit(text_surface, (x, y + 40 + i * 30))