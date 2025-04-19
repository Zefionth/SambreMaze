"""Класс для кнопок интерфейса"""
import pygame
from src.config import Config
from typing import Tuple

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, color: Tuple[int, int, int], 
                 hover_color: Tuple[int, int, int], 
                 text_color: Tuple[int, int, int] = Config.BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = pygame.font.SysFont('Arial', 24)
        self.is_hovered = False
    
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, Config.BLACK, self.rect, 2)
        
        # Автоматически выбираем контрастный цвет текста
        text_color = Config.BLACK if color == Config.WHITE or color == Config.LIGHT_GRAY else Config.WHITE
        text_surface = self.font.render(self.text, True, text_color)
        surface.blit(text_surface, (self.rect.centerx - text_surface.get_width()//2, 
                                self.rect.centery - text_surface.get_height()//2))
    
    def check_hover(self, pos: Tuple[int, int]) -> bool:
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos: Tuple[int, int], click: bool) -> bool:
        return self.rect.collidepoint(pos) and click