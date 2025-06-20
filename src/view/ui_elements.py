"""UI элементы для меню.

Этот модуль содержит классы для элементов пользовательского интерфейса:
- Button: Интерактивная кнопка
- Slider: Ползунок для выбора значений
- ColorPicker: Палитра для выбора цвета
"""

import pygame
from src.config import Config
from typing import Tuple
from pygame.event import Event


class Button:
    """Класс для создания интерактивных кнопок.
    
    Attributes:
        rect (pygame.Rect): Прямоугольная область кнопки
        text (str): Текст кнопки
        color (Tuple[int, int, int]): Основной цвет кнопки (RGB)
        hover_color (Tuple[int, int, int]): Цвет кнопки при наведении (RGB)
        is_hovered (bool): Флаг наведения курсора
        font (pygame.font.Font): Шрифт для текста кнопки
    """
    
    def __init__(
        self, 
        x: int, 
        y: int, 
        width: int, 
        height: int, 
        text: str, 
        color: Tuple[int, int, int], 
        hover_color: Tuple[int, int, int]
    ) -> None:
        """Инициализирует кнопку с заданными параметрами.
        
        Args:
            x: X-координата верхнего левого угла
            y: Y-координата верхнего левого угла
            width: Ширина кнопки
            height: Высота кнопки
            text: Текст кнопки
            color: Основной цвет (RGB)
            hover_color: Цвет при наведении (RGB)
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.SysFont(Config.FONT_NAME, Config.UI_FONT_SIZE)

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает кнопку на указанной поверхности.
        
        Args:
            surface: Поверхность для отрисовки
        """
        # цвет в зависимости от состояния наведения
        color = self.hover_color if self.is_hovered else self.color
        
        # прямоугольник кнопки
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(
            surface, 
            Config.BLACK, 
            self.rect, 
            Config.UI_BORDER_WIDTH
        )
        
        # цвет текста в зависимости от фона
        if color == Config.WHITE or color == Config.LIGHT_GRAY:
            text_color = Config.BLACK
        else:
            text_color = Config.WHITE
            
        # текст кнопки
        text_surface = self.font.render(self.text, True, text_color)
        surface.blit(
            text_surface, 
            (
                self.rect.centerx - text_surface.get_width() // 2,
                self.rect.centery - text_surface.get_height() // 2
            )
        )

    def check_hover(self, pos: Tuple[int, int]) -> bool:
        """Проверяет, находится ли курсор над кнопкой.
        
        Args:
            pos: Позиция курсора (x, y)
            
        Returns:
            bool: True если курсор над кнопкой, иначе False
        """
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(
        self, 
        pos: Tuple[int, int], 
        click: bool
    ) -> bool:
        """Проверяет, была ли нажата кнопка.
        
        Args:
            pos: Позиция курсора (x, y)
            click: Флаг нажатия кнопки мыши
            
        Returns:
            bool: True если кнопка была нажата, иначе False
        """
        return self.rect.collidepoint(pos) and click


class Slider:
    """Класс для создания ползунков (слайдеров).
    
    Attributes:
        rect (pygame.Rect): Область слайдера
        knob_rect (pygame.Rect): Область ползунка
        min (float): Минимальное значение
        max (float): Максимальное значение
        value (float): Текущее значение
        text (str): Текст слайдера
        font (pygame.font.Font): Шрифт для текста
        dragging (bool): Флаг перетаскивания ползунка
    """
    
    def __init__(
        self, 
        x: int, 
        y: int, 
        width: int, 
        height: int, 
        min_val: float, 
        max_val: float, 
        initial_val: float, 
        text: str
    ) -> None:
        """Инициализирует слайдер с заданными параметрами.
        
        Args:
            x: X-координата верхнего левого угла
            y: Y-координата верхнего левого угла
            width: Ширина слайдера
            height: Высота слайдера
            min_val: Минимальное значение
            max_val: Максимальное значение
            initial_val: Начальное значение
            text: Текст слайдера
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.knob_rect = pygame.Rect(x, y, Config.SLIDER_KNOB_WIDTH, height)
        self.min = min_val
        self.max = max_val
        self.value = initial_val
        self.text = text
        self.font = pygame.font.SysFont(Config.FONT_NAME, Config.UI_FONT_SIZE)
        self.dragging = False
        self.update_knob()

    def update_knob(self) -> None:
        """Обновляет позицию ползунка на основе текущего значения."""
        value_range = self.max - self.min
        # позиция ползунка как процент от диапазона
        knob_pos = ((self.value - self.min) / value_range) * (self.rect.width - Config.SLIDER_KNOB_WIDTH)
        self.knob_rect.x = self.rect.x + knob_pos

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает слайдер на указанной поверхности.
        
        Args:
            surface: Поверхность для отрисовки
        """
        # фон слайдера
        pygame.draw.rect(surface, Config.LIGHT_GRAY, self.rect)
        pygame.draw.rect(
            surface, 
            Config.BLACK, 
            self.rect, 
            Config.UI_BORDER_WIDTH
        )
        
        # ползунок
        pygame.draw.rect(surface, Config.BLUE, self.knob_rect)
        pygame.draw.rect(
            surface, 
            Config.BLACK, 
            self.knob_rect, 
            Config.UI_BORDER_WIDTH
        )
        
        # текст с текущим значением
        text_surface = self.font.render(
            f"{self.text}: {int(self.value)}", 
            True, 
            Config.BLACK
        )
        surface.blit(
            text_surface, 
            (self.rect.x, self.rect.y - Config.SLIDER_TEXT_OFFSET)
        )

    def handle_event(self, event: Event) -> bool:
        """Обрабатывает события слайдера.
        
        Args:
            event: Событие Pygame
            
        Returns:
            bool: True если состояние слайдера изменилось, иначе False
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.knob_rect.collidepoint(event.pos):
                self.dragging = True
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # обновление значения на основе позиции курсора
            relative_x = event.pos[0] - self.rect.x
            percentage = max(0.0, min(1.0, relative_x / self.rect.width))
            self.value = self.min + percentage * (self.max - self.min)
            self.update_knob()
            return True
            
        return False


class ColorPicker:
    """Класс для выбора цвета.
    
    Attributes:
        rect (pygame.Rect): Область пикера
        color (List[int]): Текущий цвет (RGB)
        text (str): Текст пикера
        font (pygame.font.Font): Шрифт для текста
        active (bool): Флаг активности пикера
    """
    
    def __init__(
        self, 
        x: int, 
        y: int, 
        width: int, 
        height: int, 
        color: Tuple[int, int, int], 
        text: str
    ) -> None:
        """Инициализирует пикер цвета.
        
        Args:
            x: X-координата верхнего левого угла
            y: Y-координата верхнего левого угла
            width: Ширина пикера
            height: Высота пикера
            color: Начальный цвет (RGB)
            text: Текст пикера
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = list(color)  # сохранение как списка для возможного изменения
        self.text = text
        self.font = pygame.font.SysFont(Config.FONT_NAME, Config.UI_FONT_SIZE)
        self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает пикер цвета на указанной поверхности.
        
        Args:
            surface: Поверхность для отрисовки
        """
        # прямоугольник с текущим цветом
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(
            surface, 
            Config.BLACK, 
            self.rect, 
            Config.UI_BORDER_WIDTH
        )
        
        # текст пикера
        text_surface = self.font.render(self.text, True, Config.BLACK)
        surface.blit(
            text_surface, 
            (self.rect.x, self.rect.y - Config.SLIDER_TEXT_OFFSET)
        )

    def handle_event(self, event: Event) -> bool:
        """Обрабатывает события пикера.
        
        Args:
            event: Событие Pygame
            
        Returns:
            bool: True если пикер был активирован, иначе False
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.active = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.active = False
            
        return False