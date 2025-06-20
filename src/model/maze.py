"""Генератор лабиринта.

Этот модуль содержит класс MazeGenerator, который реализует алгоритмы
генерации лабиринта, размещения опасных зон и выхода.
"""

import random
from typing import Tuple, List
from src.config import Config
from src.utils import is_valid_cell


class MazeGenerator:
    """Класс для генерации игрового лабиринта.
    
    Реализует:
    - Генерацию лабиринта алгоритмом поиска в глубину
    - Размещение стартовой зоны по центру
    - Создание выхода на границах лабиринта
    - Распределение опасных зон
    - Определение тонких стен
    """
    
    @staticmethod
    def generate_maze() -> Tuple[List[List[int]], List[List[int]], List[Tuple[int, int]], int]:
        """Генерирует лабиринт с опасными зонами и выходом.
        
        Returns:
            Tuple: 
                thin_walls: Матрица тонких стен (1 - стена, 0 - проход)
                maze: Основная матрица лабиринта (0 - проход, 1 - стена, 2 - выход)
                danger_zones: Список координат опасных зон
                cell_size: Размер ячейки лабиринта
        """
        cols = Config.WIDTH // Config.CELL_SIZE
        rows = Config.HEIGHT // Config.CELL_SIZE
        cell_size = Config.CELL_SIZE
        
        # матрицы лабиринта и тонких стен
        maze = [[1 for _ in range(cols)] for _ in range(rows)]
        thin_walls = [[0 for _ in range(cols)] for _ in range(rows)]
        
        # центральная стартовая зона
        MazeGenerator._create_start_zone(maze, cols, rows)
        
        # генерация лабиринта
        MazeGenerator._generate_with_dfs(maze, cols, rows)
        
        # создание выхода
        MazeGenerator._create_exit(maze, cols, rows)
        
        # создание опасных зон
        danger_zones = MazeGenerator._create_danger_zones(maze, cols, rows)
        
        # создание тонких стен
        MazeGenerator._create_thin_walls(maze, thin_walls, danger_zones, cols, rows)
        
        return thin_walls, maze, danger_zones, cell_size
    
    @staticmethod
    def _create_start_zone(maze: List[List[int]], cols: int, rows: int) -> None:
        """Создает стартовую зону в центре лабиринта.
        
        Args:
            maze: Матрица лабиринта
            cols: Количество колонок
            rows: Количество строк
        """
        center_x, center_y = cols // 2, rows // 2
        for y in range(center_y - Config.START_ZONE_SIZE, center_y + Config.START_ZONE_SIZE + 1):
            for x in range(center_x - Config.START_ZONE_SIZE, center_x + Config.START_ZONE_SIZE + 1):
                if is_valid_cell(x, y, maze):
                    maze[y][x] = 0
    
    @staticmethod
    def _generate_with_dfs(maze: List[List[int]], cols: int, rows: int) -> None:
        """Генерирует лабиринт с использованием алгоритма поиска в глубину.
        
        Args:
            maze: Матрица лабиринта
            cols: Количество колонок
            rows: Количество строк
        """
        center_x, center_y = cols // 2, rows // 2
        stack = [(center_x, center_y)]
        
        while stack:
            x, y = stack[-1]
            neighbors = []
            
            # проверяем возможные направления
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nx, ny = x + dx, y + dy
                if is_valid_cell(nx, ny, maze) and maze[ny][nx] == 1:
                    neighbors.append((nx, ny))
            
            if neighbors:
                nx, ny = random.choice(neighbors)
                maze[ny][nx] = 0
                maze[(ny + y) // 2][(nx + x) // 2] = 0
                stack.append((nx, ny))
            else:
                stack.pop()
    
    @staticmethod
    def _create_exit(maze: List[List[int]], cols: int, rows: int) -> None:
        """Создает выход на одной из границ лабиринта.
        
        Args:
            maze: Матрица лабиринта
            cols: Количество колонок
            rows: Количество строк
        """
        exit_side = random.randint(0, 3)
        exit_pos = {
            0: (random.randint(1, cols - 2), 0),         # верхняя граница
            1: (cols - 1, random.randint(1, rows - 2)),  # правая граница
            2: (random.randint(1, cols - 2), rows - 1),  # нижняя граница
            3: (0, random.randint(1, rows - 2))          # левая граница
        }
        exit_x, exit_y = exit_pos[exit_side]
        if is_valid_cell(exit_x, exit_y, maze):
            maze[exit_y][exit_x] = 2
    
    @staticmethod
    def _create_danger_zones(maze: List[List[int]], cols: int, rows: int) -> List[Tuple[int, int]]:
        """Создает опасные зоны на границах проходимых областей.
        
        Args:
            maze: Матрица лабиринта
            cols: Количество колонок
            rows: Количество строк
            
        Returns:
            List[Tuple[int, int]]: Список координат опасных зон
        """
        wall_cells = [
            (x, y) for y in range(rows) for x in range(cols)
            if maze[y][x] == 1 and MazeGenerator._is_border_cell(x, y, maze)
        ]
        
        return random.sample(
            wall_cells, 
            int(len(wall_cells) * Config.DANGER_ZONE_RATIO)
        )
    
    @staticmethod
    def _create_thin_walls(
        maze: List[List[int]], 
        thin_walls: List[List[int]], 
        danger_zones: List[Tuple[int, int]], 
        cols: int, 
        rows: int
    ) -> None:
        """Создает матрицу тонких стен.
        
        Args:
            maze: Основная матрица лабиринта
            thin_walls: Матрица тонких стен
            danger_zones: Список опасных зон
            cols: Количество колонок
            rows: Количество строк
        """
        for y in range(rows):
            for x in range(cols):
                if maze[y][x] == 1 and (x, y) not in danger_zones:
                    if MazeGenerator._is_border_cell(x, y, maze):
                        thin_walls[y][x] = 1
    
    @staticmethod
    def _is_border_cell(x: int, y: int, maze: List[List[int]]) -> bool:
        """Проверяет, граничит ли клетка с проходимой зоной.
        
        Args:
            x: X-координата клетки
            y: Y-координата клетки
            maze: Матрица лабиринта
            
        Returns:
            bool: True если клетка граничит с проходом, иначе False
        """
        return (
            (x > 0 and maze[y][x - 1] == 0) or 
            (x < len(maze[0]) - 1 and maze[y][x + 1] == 0) or
            (y > 0 and maze[y - 1][x] == 0) or 
            (y < len(maze) - 1 and maze[y + 1][x] == 0)
        )