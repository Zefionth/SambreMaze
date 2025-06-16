"""Генератор лабиринта"""
import random
from src.config import Config
from typing import Tuple

class MazeGenerator:
    @staticmethod
    def generate_maze() -> Tuple:
        cols = Config.WIDTH // 30
        rows = Config.HEIGHT // 30
        cell_size = 30
        
        maze = [[1 for _ in range(cols)] for _ in range(rows)]
        thin_walls = [[0 for _ in range(cols)] for _ in range(rows)]
        
        center_x, center_y = cols // 2, rows // 2
        for y in range(center_y - 1, center_y + 2):
            for x in range(center_x - 1, center_x + 2):
                if 0 <= x < cols and 0 <= y < rows:
                    maze[y][x] = 0
        
        stack = [(center_x, center_y)]
        while stack:
            x, y = stack[-1]
            neighbors = []
            for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < cols and 0 <= ny < rows and maze[ny][nx] == 1:
                    neighbors.append((nx, ny))
            
            if neighbors:
                nx, ny = random.choice(neighbors)
                maze[ny][nx] = 0
                maze[(ny+y)//2][(nx+x)//2] = 0
                stack.append((nx, ny))
            else:
                stack.pop()
        
        exit_side = random.randint(0, 3)
        exit_pos = {
            0: (random.randint(1, cols-2), 0),
            1: (cols-1, random.randint(1, rows-2)),
            2: (random.randint(1, cols-2), rows-1),
            3: (0, random.randint(1, rows-2))
        }
        exit_x, exit_y = exit_pos[exit_side]
        maze[exit_y][exit_x] = 2
        
        wall_cells = [(x,y) for y in range(rows) for x in range(cols) 
                     if maze[y][x] == 1 and ((x>0 and maze[y][x-1]==0) or 
                                            (x<cols-1 and maze[y][x+1]==0) or
                                            (y>0 and maze[y-1][x]==0) or 
                                            (y<rows-1 and maze[y+1][x]==0))]
        
        red_zones = random.sample(wall_cells, int(len(wall_cells)*0.3))
        
        for y in range(rows):
            for x in range(cols):
                if maze[y][x] == 1 and (x,y) not in red_zones:
                    if (x>0 and maze[y][x-1]==0) or (x<cols-1 and maze[y][x+1]==0) or \
                       (y>0 and maze[y-1][x]==0) or (y<rows-1 and maze[y+1][x]==0):
                        thin_walls[y][x] = 1
        
        return thin_walls, maze, red_zones, cell_size