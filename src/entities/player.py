import math

class Player:
    def __init__(self, start_pos, radius, speed):
        self.pos = list(start_pos)
        self.radius = radius
        self.speed = speed
        self.direction = 0

    def move(self, dx, dy, maze):
        new_x = self.pos[0] + dx
        new_y = self.pos[1] + dy
        
        # Check boundaries
        new_x = max(self.radius, min(new_x, maze.cell_size * len(maze.full_maze[0]) - self.radius))
        new_y = max(self.radius, min(new_y, maze.cell_size * len(maze.full_maze) - self.radius))
        
        # Check collisions
        if not maze.is_wall(new_x, new_y) and not maze.is_red_zone(new_x, new_y):
            self.pos[0] = new_x
            self.pos[1] = new_y
        
        return maze.check_exit(new_x, new_y)

    def get_direction_to(self, target_pos):
        return math.atan2(target_pos[1] - self.pos[1], target_pos[0] - self.pos[0])