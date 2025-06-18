"""Класс для визуальных частиц (эффектов)"""
from pygame import gfxdraw
from typing import Tuple, List, Optional
from src.config import Config

class Particle:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], 
                 radius: float, lifetime: float, velocity: Optional[List[float]] = None):
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.lifetime = lifetime
        self.age = 0
        self.velocity = velocity or [0, 0]
        
    def update(self, dt: float) -> bool:
        """Обновляет состояние частицы"""
        self.age += dt
        self.x += self.velocity[0] * dt * Config.PARTICLE_SPEED_FACTOR
        self.y += self.velocity[1] * dt * Config.PARTICLE_SPEED_FACTOR
        return self.age < self.lifetime
        
    def draw(self, surface) -> None:
        """Отрисовывает частицу"""
        alpha = int(255 * (1 - self.age/self.lifetime))
        color = (*self.color, alpha)
        gfxdraw.filled_circle(surface, int(self.x), int(self.y), int(self.radius), color)