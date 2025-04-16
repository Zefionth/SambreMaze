import random
import math
from maze.maze import Maze

class MazeGenerator:
    def __init__(self, config):
        self.config = config
        self.cols = config.width // config.cell_size
        self.rows = config.height // config.cell_size

    def generate(self):
        maze = [[1 for _ in range(self.cols)] for _ in range(self.rows)]
        thin_walls = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        red_zones = []

        # Create clear space around center
        center_x, center_y = self.cols // 2, self.rows // 2
        for y in range(center_y - 1, center_y + 2):
            for x in range(center_x - 1, center_x + 2):
                if 0 <= x < self.cols and 0 <= y < self.rows:
                    maze[y][x] = 0

        # Generate maze paths
        stack = [(center_x, center_y)]
        while stack:
            x, y = stack[-1]
            neighbors = self._find_unvisited_neighbors(maze, x, y)
            
            if neighbors:
                nx, ny = random.choice(neighbors)
                maze[ny][nx] = 0
                maze[(ny + y)//2][(nx + x)//2] = 0
                stack.append((nx, ny))
            else:
                stack.pop()

        # Create exit
        exit_pos = self._create_exit(maze)
        
        # Process walls and red zones
        potential_red_zones = []
        for y in range(self.rows):
            for x in range(self.cols):
                if maze[y][x] == 1:
                    if (x > 0 and maze[y][x-1] == 0) or (x < self.cols-1 and maze[y][x+1] == 0) or \
                       (y > 0 and maze[y-1][x] == 0) or (y < self.rows-1 and maze[y+1][x] == 0):
                        if abs(x - exit_pos[0]) > self.config.min_red_zone_distance_from_exit or \
                           abs(y - exit_pos[1]) > self.config.min_red_zone_distance_from_exit:
                            potential_red_zones.append((x, y))
                        thin_walls[y][x] = 1

        # Select red zones
        red_zone_count = int(len(potential_red_zones) * self.config.red_zone_percent)
        red_zones = random.sample(potential_red_zones, red_zone_count)

        return Maze(
            thin_walls=thin_walls,
            full_maze=maze,
            red_zones=red_zones,
            exit_pos=exit_pos,
            cell_size=self.config.cell_size,
            wall_thickness=self.config.wall_thickness
        )

    def _find_unvisited_neighbors(self, maze, x, y):
        neighbors = []
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.cols and 0 <= ny < self.rows and maze[ny][nx] == 1:
                neighbors.append((nx, ny))
                
        return neighbors

    def _create_exit(self, maze):
        exit_side = random.randint(0, 3)
        if exit_side == 0:  # top
            exit_x = random.randint(1, self.cols-2)
            exit_y = 0
        elif exit_side == 1:  # right
            exit_x = self.cols - 1
            exit_y = random.randint(1, self.rows-2)
        elif exit_side == 2:  # bottom
            exit_x = random.randint(1, self.cols-2)
            exit_y = self.rows - 1
        else:  # left
            exit_x = 0
            exit_y = random.randint(1, self.rows-2)
            
        maze[exit_y][exit_x] = 2
        return (exit_x, exit_y)