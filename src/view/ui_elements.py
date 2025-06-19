"""UI элементы для меню"""
import pygame
from src.config import Config
from typing import Tuple

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, 
                text: str, color: Tuple[int, int, int], 
                hover_color: Tuple[int, int, int]):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.font = pygame.font.SysFont(Config.FONT_NAME, Config.UI_FONT_SIZE)

    def draw(self, surface):
        """Отрисовывает кнопку"""
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, Config.BLACK, self.rect, Config.UI_BORDER_WIDTH)
        
        text_color = Config.BLACK if color == Config.WHITE or color == Config.LIGHT_GRAY else Config.WHITE
        text_surface = self.font.render(self.text, True, text_color)
        surface.blit(text_surface, (
            self.rect.centerx - text_surface.get_width()//2,
            self.rect.centery - text_surface.get_height()//2
        ))

    def check_hover(self, pos: Tuple[int, int]) -> bool:
        """Проверяет наведение курсора"""
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos: Tuple[int, int], click: bool) -> bool:
        """Проверяет клик по кнопке"""
        return self.rect.collidepoint(pos) and click

class Slider:
    def __init__(self, x: int, y: int, width: int, height: int, 
                min_val: float, max_val: float, initial_val: float, text: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.knob_rect = pygame.Rect(x, y, Config.SLIDER_KNOB_WIDTH, height)
        self.min = min_val
        self.max = max_val
        self.value = initial_val
        self.text = text
        self.font = pygame.font.SysFont(Config.FONT_NAME, Config.UI_FONT_SIZE)
        self.dragging = False
        self.update_knob()

    def update_knob(self):
        """Обновляет позицию ползунка"""
        value_range = self.max - self.min
        knob_pos = ((self.value - self.min) / value_range) * (self.rect.width - Config.SLIDER_KNOB_WIDTH)
        self.knob_rect.x = self.rect.x + knob_pos

    def draw(self, surface):
        """Отрисовывает слайдер"""
        pygame.draw.rect(surface, Config.LIGHT_GRAY, self.rect)
        pygame.draw.rect(surface, Config.BLACK, self.rect, Config.UI_BORDER_WIDTH)
        pygame.draw.rect(surface, Config.BLUE, self.knob_rect)
        pygame.draw.rect(surface, Config.BLACK, self.knob_rect, Config.UI_BORDER_WIDTH)
        
        text_surface = self.font.render(f"{self.text}: {int(self.value)}", True, Config.BLACK)
        surface.blit(text_surface, (self.rect.x, self.rect.y - Config.SLIDER_TEXT_OFFSET))

    def handle_event(self, event) -> bool:
        """Обрабатывает события слайдера"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.knob_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            relative_x = event.pos[0] - self.rect.x
            percentage = max(0, min(1, relative_x / self.rect.width))
            self.value = self.min + percentage * (self.max - self.min)
            self.update_knob()
            return True
        return False

class ColorPicker:
    def __init__(self, x: int, y: int, width: int, height: int, 
                color: Tuple[int, int, int], text: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = list(color)
        self.text = text
        self.font = pygame.font.SysFont(Config.FONT_NAME, Config.UI_FONT_SIZE)
        self.active = False

    def draw(self, surface):
        """Отрисовывает пикер цвета"""
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, Config.BLACK, self.rect, Config.UI_BORDER_WIDTH)
        
        text_surface = self.font.render(self.text, True, Config.BLACK)
        surface.blit(text_surface, (self.rect.x, self.rect.y - Config.SLIDER_TEXT_OFFSET))

    def handle_event(self, event) -> bool:
        """Обрабатывает события пикера"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.active = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.active = False
        return False