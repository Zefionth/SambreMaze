"""Модуль для сканеров (локатор, детектор).

Этот модуль содержит базовый класс Scanner и его реализации:
- LocatorScanner: для точечного сканирования стен
- DetectorScanner: для широкого сканирования опасных зон
"""

import pygame
import math
import random
from src.config import Config
from typing import List, Tuple, Any
from src.utils import is_valid_cell


class Scanner:
    """Базовый класс для игровых сканеров.
    
    Реализует общую логику для сканеров:
    - Определение клетки по позиции
    - Проверку валидности клетки
    - Проверку типа клетки (стена, опасная зона)
    
    Attributes:
        game_model (GameModel): Ссылка на модель игры
        last_scan_time (int): Время последнего сканирования (в мс)
    """
    
    def __init__(self, game_model: Any) -> None:
        """Инициализирует сканер с ссылкой на модель игры.
        
        Args:
            game_model: Экземпляр GameModel
        """
        self.game_model = game_model
        self.last_scan_time = 0

    def scan(self, start_pos: Tuple[float, float], angle: float) -> Any:
        """Выполняет сканирование в заданном направлении.
        
        Должен быть реализован в подклассах.
        
        Args:
            start_pos: Начальная позиция сканирования (x, y)
            angle: Угол сканирования в радианах
            
        Raises:
            NotImplementedError: Если метод не переопределен в подклассе
        """
        raise NotImplementedError("Subclasses must implement this method")
        
    def _get_cell_at_position(self, x: float, y: float) -> Tuple[int, int]:
        """Возвращает координаты клетки по позиции.
        
        Args:
            x: X-координата позиции
            y: Y-координата позиции
            
        Returns:
            Tuple[int, int]: Координаты клетки (cell_x, cell_y)
        """
        return int(x) // self.game_model.cell_size, int(y) // self.game_model.cell_size
        
    def _is_valid_cell(self, cell_x: int, cell_y: int) -> bool:
        """Проверяет, находится ли клетка в пределах лабиринта.
        
        Args:
            cell_x: X-координата клетки
            cell_y: Y-координата клетки
            
        Returns:
            bool: True если клетка валидна, иначе False
        """
        return is_valid_cell(cell_x, cell_y, self.game_model.maze)
        
    def _is_wall(self, cell_x: int, cell_y: int) -> bool:
        """Проверяет, является ли клетка стеной.
        
        Args:
            cell_x: X-координата клетки
            cell_y: Y-координата клетки
            
        Returns:
            bool: True если клетка является стеной, иначе False
        """
        if not self._is_valid_cell(cell_x, cell_y):
            return False
        return self.game_model.thin_walls[cell_y][cell_x] == 1
        
    def _is_danger_zone(self, cell_x: int, cell_y: int) -> bool:
        """Проверяет, является ли клетка опасной зоной.
        
        Args:
            cell_x: X-координата клетки
            cell_y: Y-координата клетки
            
        Returns:
            bool: True если клетка опасна, иначе False
        """
        return (cell_x, cell_y) in self.game_model.danger_zones


class LocatorScanner(Scanner):
    """Реализация сканера для локатора (точечное сканирование)."""
    
    def scan(
        self, 
        start_pos: Tuple[float, float], 
        angle: float
    ) -> List[Tuple[float, float, int]]:
        """Выполняет точечное сканирование в заданном направлении.
        
        Args:
            start_pos: Начальная позиция сканирования (x, y)
            angle: Угол сканирования в радианах
            
        Returns:
            List[Tuple[float, float, int]]: Список обнаруженных точек 
                                            (x, y, время создания)
        """
        current_time = pygame.time.get_ticks()
        
        # проверка времени перезарядки
        if current_time - self.last_scan_time < self.game_model.settings['locator_cooldown']:
            return []
            
        self.last_scan_time = current_time
        
        # случайное отклонение
        angle += random.uniform(
            -Config.LOCATOR_ANGLE_VARIATION, 
            Config.LOCATOR_ANGLE_VARIATION
        )
        
        closest_hit = None
        closest_dist = float('inf')
        
        # скан лучом до первой преграды
        for dist in range(5, Config.LOCATOR_SCAN_LENGTH, Config.LOCATOR_SCAN_STEP):
            x = start_pos[0] + math.cos(angle) * dist
            y = start_pos[1] + math.sin(angle) * dist
            
            cell_x, cell_y = self._get_cell_at_position(x, y)
            
            # проверка, является ли клетка стеной или выходом
            if self._is_valid_cell(cell_x, cell_y) and (
                self._is_wall(cell_x, cell_y) or 
                self.game_model.maze[cell_y][cell_x] == 2
            ):
                if dist < closest_dist:
                    closest_dist = dist
                    closest_hit = (x, y, cell_x, cell_y)
                break
        
        # если найдено столкновение, создаем точку с небольшим смещением
        if closest_hit:
            x, y, cell_x, cell_y = closest_hit
            normal = self.game_model.get_wall_normal(cell_x, cell_y, x, y)
            
            # случайное смещение для визуального эффекта
            offset_x = normal[0] * random.uniform(
                -Config.LOCATOR_HIT_VARIATION, 
                Config.LOCATOR_HIT_VARIATION
            )
            offset_y = normal[1] * random.uniform(
                -Config.LOCATOR_HIT_VARIATION, 
                Config.LOCATOR_HIT_VARIATION
            )
            
            return [(
                x + offset_x,
                y + offset_y,
                current_time
            )]
            
        return []


class DetectorScanner(Scanner):
    """Реализация сканера для детектора (широкое сканирование)."""
    
    def scan(
        self, 
        start_pos: Tuple[float, float], 
        angle: float
    ) -> Tuple[List[Tuple[float, float, int]], List[Tuple[float, float]]]:
        """Выполняет широкое сканирование в заданном направлении.
        
        Args:
            start_pos: Начальная позиция сканирования (x, y)
            angle: Угол сканирования в радианах
            
        Returns:
            Tuple: 
                - Список точек волны (x, y, время)
                - Список позиций опасных зон (x, y)
        """
        current_time = pygame.time.get_ticks()
        
        # проверка времени перезарядки
        if current_time - self.last_scan_time < self.game_model.settings['detector_cooldown']:
            return [], []
            
        self.last_scan_time = current_time
        wave_points = []
        hit_positions = []
        
        # скан в конусе с разными углами
        for delta in range(Config.DETECTOR_ANGLE_MIN, Config.DETECTOR_ANGLE_MAX, Config.DETECTOR_ANGLE_STEP):
            current_angle = angle + math.radians(delta)
            
            # скан лучом до преграды
            for dist in range(0, Config.DETECTOR_SCAN_LENGTH, Config.DETECTOR_SCAN_STEP):
                x = start_pos[0] + math.cos(current_angle) * dist
                y = start_pos[1] + math.sin(current_angle) * dist
                cell_x, cell_y = self._get_cell_at_position(x, y)

                # прерываем луч при выходе за границы
                if not self._is_valid_cell(cell_x, cell_y):
                    break

                # добавление точку в волну
                wave_points.append((x, y, current_time))

                # проверка опасных зоны
                if self._is_danger_zone(cell_x, cell_y):
                    hit_positions.append((x, y))
                
                # прерываем луч при столкновении со стеной
                if self._is_wall(cell_x, cell_y) or self.game_model.maze[cell_y][cell_x] == 1:
                    break
            
        return wave_points, hit_positions