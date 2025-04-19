"""Класс для выбора цвета"""
import pygame
from src.config import Config
from typing import Tuple

class ColorPicker:
    def __init__(self, x: int, y: int, width: int, height: int, 
                 color: Tuple[int, int, int], text: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = list(color)
        self.text = text
        self.font = pygame.font.SysFont('Arial', 20)
        self.active = False
    
    def draw(self, surface) -> None:
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, Config.BLACK, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, Config.BLACK)
        surface.blit(text_surface, (self.rect.x, self.rect.y - 25))
    
    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.active = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.active = False
        return False
    
    def update_color(self, component: int, value: int) -> Tuple[int, int, int]:
        self.color[component] = max(0, min(255, value))
        return tuple(self.color)