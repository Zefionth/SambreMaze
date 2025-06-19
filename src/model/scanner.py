"""Модуль для сканеров (локатор, детектор)"""
import pygame
import math
import random
from src.config import Config
from typing import List, Tuple, Optional
from src.utils import is_valid_cell

class Scanner:
    def __init__(self, game_model):
        self.game_model = game_model
        self.last_scan_time = 0

    def scan(self, start_pos: Tuple[float, float], angle: float):
        """Базовый метод сканирования"""
        raise NotImplementedError("Subclasses must implement this method")
        
    def _get_cell_at_position(self, x: float, y: float) -> Tuple[int, int]:
        """Возвращает координаты клетки по позиции"""
        return int(x) // self.game_model.cell_size, int(y) // self.game_model.cell_size
        
    def _is_valid_cell(self, cell_x: int, cell_y: int) -> bool:
        """Проверяет, находится ли клетка в пределах лабиринта"""
        return is_valid_cell(cell_x, cell_y, self.game_model.maze)
        
    def _is_wall(self, cell_x: int, cell_y: int) -> bool:
        """Проверяет, является ли клетка стеной"""
        if not self._is_valid_cell(cell_x, cell_y):
            return False
        # Проверяем только тонкие стены для коллизий
        return self.game_model.thin_walls[cell_y][cell_x] == 1
        
    def _is_danger_zone(self, cell_x: int, cell_y: int) -> bool:
        """Проверяет, является ли клетка опасной зоной"""
        return (cell_x, cell_y) in self.game_model.danger_zones

class LocatorScanner(Scanner):
    def scan(self, start_pos: Tuple[float, float], angle: float) -> List[Tuple[float, float, int]]:
        current_time = pygame.time.get_ticks()
        if current_time - self.last_scan_time < self.game_model.settings['locator_cooldown']:
            return []
            
        self.last_scan_time = current_time
        angle += random.uniform(-Config.LOCATOR_ANGLE_VARIATION, Config.LOCATOR_ANGLE_VARIATION)
        
        closest_hit = None
        closest_dist = float('inf')
        
        for dist in range(5, Config.LOCATOR_SCAN_LENGTH, Config.LOCATOR_SCAN_STEP):
            x = start_pos[0] + math.cos(angle) * dist
            y = start_pos[1] + math.sin(angle) * dist
            
            cell_x, cell_y = self._get_cell_at_position(x, y)
            if self._is_valid_cell(cell_x, cell_y) and (self._is_wall(cell_x, cell_y) or 
                                                      self.game_model.maze[cell_y][cell_x] == 2):
                if dist < closest_dist:
                    closest_dist = dist
                    closest_hit = (x, y, cell_x, cell_y)
                break
        
        if closest_hit:
            x, y, cell_x, cell_y = closest_hit
            normal = self.game_model.get_wall_normal(cell_x, cell_y, x, y)
            return [(
                x + normal[0] * random.uniform(-Config.LOCATOR_HIT_VARIATION, Config.LOCATOR_HIT_VARIATION),
                y + normal[1] * random.uniform(-Config.LOCATOR_HIT_VARIATION, Config.LOCATOR_HIT_VARIATION),
                current_time
            )]
        return []

class DetectorScanner(Scanner):
    def scan(self, start_pos: Tuple[float, float], angle: float) -> Tuple[List[Tuple[float, float, int]], List[Tuple[float, float]]]:
        current_time = pygame.time.get_ticks()
        if current_time - self.last_scan_time < self.game_model.settings['detector_cooldown']:
            return [], []
            
        self.last_scan_time = current_time
        wave_points = []
        hit_positions = []
        
        for delta in range(Config.DETECTOR_ANGLE_MIN, Config.DETECTOR_ANGLE_MAX, Config.DETECTOR_ANGLE_STEP):
            current_angle = angle + math.radians(delta)
            
            for dist in range(0, Config.DETECTOR_SCAN_LENGTH, Config.DETECTOR_SCAN_STEP):
                x = start_pos[0] + math.cos(current_angle) * dist
                y = start_pos[1] + math.sin(current_angle) * dist
                cell_x, cell_y = self._get_cell_at_position(x, y)

                if not self._is_valid_cell(cell_x, cell_y):
                    break

                wave_points.append((x, y, current_time))

                # Проверяем опасные зоны независимо от стен
                if self._is_danger_zone(cell_x, cell_y):
                    hit_positions.append((x, y))
                
                # Останавливаем луч только на стенах
                if self._is_wall(cell_x, cell_y) or self.game_model.maze[cell_y][cell_x] == 1:
                    break
            
        return wave_points, hit_positions