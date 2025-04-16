class Maze:
    def __init__(self, thin_walls, full_maze, red_zones, exit_pos, cell_size, wall_thickness):
        self.thin_walls = thin_walls
        self.full_maze = full_maze
        self.red_zones = red_zones
        self.exit_pos = exit_pos
        self.cell_size = cell_size
        self.wall_thickness = wall_thickness

    def is_wall(self, x, y):
        cell_x = x // self.cell_size
        cell_y = y // self.cell_size
        if 0 <= cell_x < len(self.full_maze[0]) and 0 <= cell_y < len(self.full_maze):
            return self.thin_walls[cell_y][cell_x] == 1
        return False

    def is_red_zone(self, x, y):
        cell_x = x // self.cell_size
        cell_y = y // self.cell_size
        return (cell_x, cell_y) in self.red_zones

    def check_exit(self, x, y):
        cell_x = x // self.cell_size
        cell_y = y // self.cell_size
        exit_x, exit_y = self.exit_pos
        return cell_x == exit_x and cell_y == exit_y