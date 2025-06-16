"""Модель игрока"""

from src.config import Config

class Player:
    def __init__(self, settings: dict):
        self.pos = [Config.WIDTH // 2, Config.HEIGHT // 2]
        self.radius = settings.get('player_radius', 10)
        self.speed = settings.get('player_speed', 3.5)
        self.speed_diagonal = self.speed * 0.7071
        self.glow = 0
        self.color = settings['colors']['player']
    
    def update_position(self, dx: float, dy: float, game_state: dict) -> None:
        if game_state['game_over'] or game_state['game_won']:
            return
        
        new_pos = self.pos.copy()
        thin_walls = game_state['thin_walls']
        cell_size = game_state['cell_size']
        
        # Проверка столкновений по X и Y отдельно
        if dx != 0:
            new_pos[0] += dx
            cell_x = int(new_pos[0]) // cell_size
            cell_y = int(self.pos[1]) // cell_size
            if 0 <= cell_x < len(thin_walls[0]) and 0 <= cell_y < len(thin_walls):
                if thin_walls[cell_y][cell_x] == 1:
                    new_pos[0] = self.pos[0]
        
        if dy != 0:
            new_pos[1] += dy
            cell_x = int(new_pos[0]) // cell_size
            cell_y = int(new_pos[1]) // cell_size
            if 0 <= cell_x < len(thin_walls[0]) and 0 <= cell_y < len(thin_walls):
                if thin_walls[cell_y][cell_x] == 1:
                    new_pos[1] = self.pos[1]
        
        # Проверка столкновений углов
        corners = [
            (new_pos[0]-self.radius, new_pos[1]-self.radius),
            (new_pos[0]+self.radius, new_pos[1]+self.radius),
            (new_pos[0]-self.radius, new_pos[1]+self.radius),
            (new_pos[0]+self.radius, new_pos[1]-self.radius)
        ]
        
        can_move = True
        for x, y in corners:
            cell_x, cell_y = int(x)//cell_size, int(y)//cell_size
            if 0 <= cell_x < len(thin_walls[0]) and 0 <= cell_y < len(thin_walls):
                if thin_walls[cell_y][cell_x] == 1:
                    can_move = False
                    break
        
        if can_move:
            self.pos = new_pos
    
    def update_glow(self, dt: float) -> None:
        self.glow = max(0, self.glow - dt * 5)