"""Генератор лабиринта"""
import random
from src.config import Config
from src.utils import is_valid_cell
from typing import Tuple

class MazeGenerator:
    @staticmethod
    def generate_maze() -> Tuple:
        """Генерирует лабиринт с опасными зонами и выходом"""
        cols = Config.WIDTH // Config.CELL_SIZE
        rows = Config.HEIGHT // Config.CELL_SIZE
        cell_size = Config.CELL_SIZE
        
        maze = [[1 for _ in range(cols)] for _ in range(rows)]
        thin_walls = [[0 for _ in range(cols)] for _ in range(rows)]
        
        # Создаем центральную стартовую зону
        center_x, center_y = cols // 2, rows // 2
        for y in range(center_y - Config.START_ZONE_SIZE, center_y + Config.START_ZONE_SIZE + 1):
            for x in range(center_x - Config.START_ZONE_SIZE, center_x + Config.START_ZONE_SIZE + 1):
                if is_valid_cell(x, y, maze):
                    maze[y][x] = 0
        
        # Генерация лабиринта алгоритмом поиска в глубину
        stack = [(center_x, center_y)]
        while stack:
            x, y = stack[-1]
            neighbors = []
            for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
                nx, ny = x + dx, y + dy
                if is_valid_cell(nx, ny, maze) and maze[ny][nx] == 1:
                    neighbors.append((nx, ny))
            
            if neighbors:
                nx, ny = random.choice(neighbors)
                maze[ny][nx] = 0
                maze[(ny+y)//2][(nx+x)//2] = 0
                stack.append((nx, ny))
            else:
                stack.pop()
        
        # Создание выхода
        exit_side = random.randint(0, 3)
        exit_pos = {
            0: (random.randint(1, cols-2), 0),
            1: (cols-1, random.randint(1, rows-2)),
            2: (random.randint(1, cols-2), rows-1),
            3: (0, random.randint(1, rows-2))
        }
        exit_x, exit_y = exit_pos[exit_side]
        if is_valid_cell(exit_x, exit_y, maze):
            maze[exit_y][exit_x] = 2
        
        # Создание опасных зон
        wall_cells = [(x,y) for y in range(rows) for x in range(cols) 
                     if maze[y][x] == 1 and MazeGenerator._is_border_cell(x, y, maze)]
        
        red_zones = random.sample(wall_cells, int(len(wall_cells) * Config.DANGER_ZONE_RATIO))
        
        # Создание тонких стен
        for y in range(rows):
            for x in range(cols):
                if maze[y][x] == 1 and (x,y) not in red_zones:
                    if MazeGenerator._is_border_cell(x, y, maze):
                        thin_walls[y][x] = 1
        
        return thin_walls, maze, red_zones, cell_size
    
    @staticmethod
    def _is_border_cell(x: int, y: int, maze: list) -> bool:
        """Проверяет, граничит ли клетка с проходимой зоной"""
        return ((x > 0 and maze[y][x-1] == 0) or 
                (x < len(maze[0])-1 and maze[y][x+1] == 0) or
                (y > 0 and maze[y-1][x] == 0) or 
                (y < len(maze)-1 and maze[y+1][x] == 0))