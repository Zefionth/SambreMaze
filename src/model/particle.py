"""Класс для визуальных частиц (эффектов).

Этот модуль содержит класс Particle, который реализует поведение
и отрисовку визуальных частиц для игровых эффектов.
"""

from pygame import gfxdraw
from typing import Tuple, List, Optional
from src.config import Config
import pygame


class Particle:
    """Класс для представления визуальных частиц.
    
    Частицы используются для создания различных визуальных эффектов:
    - Следы от сканирования
    - Эффекты столкновений
    - Анимации победы/поражения
    
    Attributes:
        x (float): X-координата центра частицы
        y (float): Y-координата центра частицы
        color (Tuple[int, int, int]): Базовый цвет частицы (RGB)
        radius (float): Начальный радиус частицы
        lifetime (float): Полное время жизни частицы в секундах
        age (float): Текущий возраст частицы в секундах
        velocity (List[float]): Вектор скорости частицы [vx, vy]
    """
    
    def __init__(
        self, 
        x: float, 
        y: float, 
        color: Tuple[int, int, int], 
        radius: float, 
        lifetime: float, 
        velocity: Optional[List[float]] = None
    ) -> None:
        """Инициализирует частицу с заданными параметрами.
        
        Args:
            x: Начальная X-координата
            y: Начальная Y-координата
            color: Базовый цвет (RGB)
            radius: Начальный радиус
            lifetime: Время жизни в секундах
            velocity: Начальная скорость [vx, vy] (по умолчанию [0, 0])
        """
        self.x = x
        self.y = y
        self.color = color
        self.radius = radius
        self.lifetime = lifetime
        self.age = 0.0
        self.velocity = velocity or [0.0, 0.0]
        
    def update(self, dt: float) -> bool:
        """Обновляет состояние частицы.
        
        Args:
            dt: Время, прошедшее с предыдущего обновления (в секундах)
            
        Returns:
            bool: True если частица еще "жива", False если время истекло
        """
        self.age += dt
        
        # обновление позиции на основе скорости
        self.x += self.velocity[0] * dt * Config.PARTICLE_SPEED_FACTOR
        self.y += self.velocity[1] * dt * Config.PARTICLE_SPEED_FACTOR
        
        # проверка времени жизни
        return self.age < self.lifetime
        
    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает частицу на указанной поверхности.
        
        Args:
            surface: Поверхность Pygame для отрисовки
        """
        # рассчитываем прозрачность на основе оставшегося времени жизни
        alpha = int(255 * (1 - self.age / self.lifetime))
        
        particle_color = (*self.color, alpha)
        
        # отрисовываем частицу как заполненный круг
        gfxdraw.filled_circle(
            surface, 
            int(self.x), 
            int(self.y), 
            int(self.radius), 
            particle_color
        )