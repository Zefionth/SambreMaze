"""Класс для слайдеров настроек"""
import pygame
from src.config import Config

class Slider:
    def __init__(self, x: int, y: int, width: int, height: int, 
                 min_val: float, max_val: float, initial_val: float, 
                 text: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.knob_rect = pygame.Rect(x, y, 20, height)
        self.min = min_val
        self.max = max_val
        self.value = initial_val
        self.text = text
        self.font = pygame.font.SysFont('Arial', 20)
        self.dragging = False
        self.update_knob()
    
    def update_knob(self) -> None:
        value_range = self.max - self.min
        knob_pos = ((self.value - self.min) / value_range) * (self.rect.width - 20)
        self.knob_rect.x = self.rect.x + knob_pos
    
    def draw(self, surface):
        # Фон слайдера
        pygame.draw.rect(surface, Config.LIGHT_GRAY, self.rect)
        pygame.draw.rect(surface, Config.BLACK, self.rect, 2)
        
        # Ползунок
        pygame.draw.rect(surface, Config.BLUE, self.knob_rect)
        pygame.draw.rect(surface, Config.BLACK, self.knob_rect, 2)
        
        # Текст - всегда черный для читаемости на светлом фоне
        text_surface = self.font.render(f"{self.text}: {int(self.value)}", True, Config.BLACK)
        surface.blit(text_surface, (self.rect.x, self.rect.y - 25))
    
    def handle_event(self, event) -> bool:
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