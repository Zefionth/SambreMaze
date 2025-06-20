"""Модель игрового состояния.

Этот модуль содержит класс GameModel, который управляет состоянием игры,
включая игрока, лабиринт, частицы, сканеры и логику игры.
"""

from src.model.path_finder import PathFinder
from src.model.player import Player
from src.model.maze import MazeGenerator
from src.model.particle import Particle
from src.model.scanner import LocatorScanner, DetectorScanner
from src.utils import is_valid_cell
from src.config import Config
from typing import List, Tuple, Dict, Optional, Any
import pygame
import math


class GameModel:
    """Основная модель игрового состояния.
    
    Отвечает за:
    - Управление состоянием игрока
    - Генерацию и управление лабиринтом
    - Обработку сканирования локатором и детектором
    - Управление частицами и визуальными эффектами
    - Проверку условий победы/поражения
    - Поиск пути к выходу
    
    Attributes:
        settings (dict): Текущие настройки игры
        show_path (bool): Флаг отображения пути к выходу
        path (List[Tuple[int, int]]): Рассчитанный путь к выходу
        player (Player): Объект игрока
        thin_walls (List[List[int]]): Матрица тонких стен
        maze (List[List[int]]): Матрица лабиринта
        danger_zones (List[Tuple[int, int]]): Список опасных зон
        cell_size (int): Размер ячейки лабиринта
        particles (List[Particle]): Список активных частиц
        locator_points (List[Tuple[float, float, int]]): Точки локатора
        detector_points (List[Tuple[float, float, int]]): Точки детектора
        detector_lines (List[Dict]): Линии волн детектора
        game_won (bool): Флаг победы в игре
        game_over (bool): Флаг поражения в игре
        left_mouse_down (bool): Флаг нажатия ЛКМ
        locator_scanner (LocatorScanner): Сканер локатора
        detector_scanner (DetectorScanner): Сканер детектора
    """
    
    def __init__(self, settings: Dict[str, Any]) -> None:
        """Инициализирует модель игры с заданными настройками.
        
        Args:
            settings: Словарь настроек игры
        """
        self.settings = settings
        self.reset()
        self.show_path = False
        self.path: List[Tuple[int, int]] = []
    
    def reset(self) -> None:
        """Сбрасывает игровое состояние к начальным значениям."""
        self.player = Player(self.settings)
        self.thin_walls, self.maze, self.danger_zones, self.cell_size = MazeGenerator.generate_maze()
        
        self.particles: List[Particle] = []
        self.locator_points: List[Tuple[float, float, int]] = []
        self.detector_points: List[Tuple[float, float, int]] = []
        self.detector_lines: List[Dict] = []
        
        self.game_won = False
        self.game_over = False
        self.left_mouse_down = False
        
        self.locator_scanner = LocatorScanner(self)
        self.detector_scanner = DetectorScanner(self)
    
    def update(self, dt: float, mouse_pos: Tuple[int, int], keys_pressed: List[bool]) -> None:
        """Обновляет состояние игры.
        
        Args:
            dt: Время, прошедшее с предыдущего обновления (в секундах)
            mouse_pos: Позиция курсора мыши (x, y)
            keys_pressed: Состояние нажатых клавиш
        """
        current_time = pygame.time.get_ticks()
        self._handle_locator_scan(current_time, mouse_pos)
        self._handle_player_movement(keys_pressed)
        self._check_game_status()
        self._update_particles_and_points(dt, current_time)

    def _handle_locator_scan(self, current_time: int, mouse_pos: Tuple[int, int]) -> None:
        """Обрабатывает сканирование локатором.
        
        Args:
            current_time: Текущее время в миллисекундах
            mouse_pos: Позиция курсора мыши (x, y)
        """
        if self.left_mouse_down:
            angle = math.atan2(
                mouse_pos[1] - self.player.pos[1],
                mouse_pos[0] - self.player.pos[0]
            )
            new_points = self.locator_scanner.scan(self.player.pos, angle)
            
            if new_points:
                self.locator_points.extend(new_points)
                self.player.glow = min(
                    Config.MAX_GLOW, 
                    self.player.glow + Config.GLOW_INCREASE
                )
                
                # Создаем частицу в точке сканирования
                px, py, pt = new_points[0]
                part_angle = math.atan2(
                    py - self.player.pos[1], 
                    px - self.player.pos[0]
                )
                self.particles.append(Particle(
                    px, py, 
                    self.settings['colors']['locator'], 
                    Config.PARTICLE_SIZE, 
                    Config.PARTICLE_LIFETIME,
                    [
                        math.cos(part_angle) * Config.PARTICLE_SPEED,
                        math.sin(part_angle) * Config.PARTICLE_SPEED
                    ]
                ))

    def _handle_player_movement(self, keys_pressed: List[bool]) -> None:
        """Обрабатывает движение игрока на основе нажатых клавиш.
        
        Args:
            keys_pressed: Состояние нажатых клавиш
        """
        move_x = keys_pressed[pygame.K_d] - keys_pressed[pygame.K_a]
        move_y = keys_pressed[pygame.K_s] - keys_pressed[pygame.K_w]
        
        game_state = {
            'thin_walls': self.thin_walls,
            'cell_size': self.cell_size,
            'game_over': self.game_over,
            'game_won': self.game_won
        }
        
        self.player.update_position(move_x, move_y, game_state)

    def _check_game_status(self) -> None:
        """Проверяет условия победы или поражения."""
        cell_x = int(self.player.pos[0] // self.cell_size)
        cell_y = int(self.player.pos[1] // self.cell_size)
        
        if is_valid_cell(cell_x, cell_y, self.maze):
            if (cell_x, cell_y) in self.danger_zones and not self.game_over:
                self._trigger_game_over()
            elif self.maze[cell_y][cell_x] == 2 and not self.game_won:
                self.game_won = True
    
    def _trigger_game_over(self) -> None:
        """Активирует состояние поражения и создает эффекты."""
        self.game_over = True
        self.particles.append(Particle(
            self.player.pos[0], self.player.pos[1], 
            Config.RED,
            Config.GAMEOVER_PARTICLE_SIZE, 
            Config.GAMEOVER_PARTICLE_LIFETIME
        ))

    def _update_particles_and_points(self, dt: float, current_time: int) -> None:
        """Обновляет состояние частиц и временных точек.
        
        Args:
            dt: Время, прошедшее с предыдущего обновления (в секундах)
            current_time: Текущее время в миллисекундах
        """
        # обновление частиц
        self.particles = [p for p in self.particles if p.update(dt)]
        
        # обновление свечения игрока
        self.player.update_glow(dt)
        
        # удаление устаревших точек локатора
        self.locator_points = [
            (x, y, t) for x, y, t in self.locator_points 
            if current_time - t < self.settings['point_lifetime']
        ]
        
        # удаление устаревших точек детектора
        self.detector_points = [
            (x, y, t) for x, y, t in self.detector_points 
            if current_time - t < self.settings['point_lifetime']
        ]

    def get_wall_normal(
        self, 
        cell_x: int, 
        cell_y: int, 
        hit_x: float, 
        hit_y: float
    ) -> Tuple[int, int]:
        """Определяет нормаль стены в точке столкновения.
        
        Args:
            cell_x: X-координата ячейки
            cell_y: Y-координата ячейки
            hit_x: X-координата точки столкновения
            hit_y: Y-координата точки столкновения
            
        Returns:
            Tuple[int, int]: Вектор нормали к стене
        """
        cell_left = cell_x * self.cell_size
        cell_right = (cell_x + 1) * self.cell_size
        cell_top = cell_y * self.cell_size
        cell_bottom = (cell_y + 1) * self.cell_size
        
        # расчет расстояния до границ ячейки
        dists = {
            'left': abs(hit_x - cell_left),
            'right': abs(hit_x - cell_right),
            'top': abs(hit_y - cell_top),
            'bottom': abs(hit_y - cell_bottom)
        }
        
        # ближайшая граница
        min_side = min(dists, key=dists.get)
        if min_side == 'left': 
            return (1, 0)
        elif min_side == 'right': 
            return (-1, 0)
        elif min_side == 'top': 
            return (0, 1)
        else: 
            return (0, -1)
    
    def add_detector_wave(
        self, 
        start_pos: Tuple[float, float], 
        angle: float
    ) -> Tuple[List[Tuple[float, float, int]], List[Tuple[float, float]]]:
        """Добавляет волну детектора в указанном направлении.
        
        Args:
            start_pos: Начальная позиция волны (x, y)
            angle: Угол направления волны в радианах
            
        Returns:
            Tuple: 
                - Список точек волны
                - Список позиций обнаруженных опасных зон
        """
        return self.detector_scanner.scan(start_pos, angle)

    def find_path_to_exit(self) -> None:
        """Находит путь к выходу с помощью алгоритма A*."""
        start_x = int(self.player.pos[0] // self.cell_size)
        start_y = int(self.player.pos[1] // self.cell_size)
        exit_pos = self._find_exit_position()
        
        if exit_pos:
            self.path = PathFinder.find_path(
                (start_x, start_y), 
                exit_pos, 
                self.maze
            )

    def _find_exit_position(self) -> Optional[Tuple[int, int]]:
        """Находит позицию выхода в лабиринте.
        
        Returns:
            Optional[Tuple[int, int]]: Координаты выхода или None
        """
        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                if self.maze[y][x] == 2:
                    return (x, y)
        return None