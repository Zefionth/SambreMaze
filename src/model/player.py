"""Модель игрока"""
from src.config import Config
from src.utils import is_valid_cell

class Player:
    def __init__(self, settings: dict):
        self.pos = [Config.WIDTH // 2, Config.HEIGHT // 2]
        self.radius = settings.get('player_radius', Config.DEFAULT_SETTINGS['player_radius'])
        self.speed = settings.get('player_speed', Config.DEFAULT_SETTINGS['player_speed'])
        self.speed_diagonal = self.speed * Config.DIAGONAL_FACTOR
        self.glow = 0
        self.color = settings['colors']['player']
        self.last_valid_pos = self.pos.copy()
    
    def update_position(self, dx: float, dy: float, game_state: dict) -> None:
        """Обновляет позицию игрока с учетом коллизий"""
        if game_state['game_over'] or game_state['game_won']:
            return
        
        # Сохраняем последнюю валидную позицию
        self.last_valid_pos = self.pos.copy()
        
        # Рассчитываем новую позицию
        new_pos = self._calculate_new_position(dx, dy)
        
        # Проверяем коллизии
        if not self._check_collision(new_pos, game_state):
            self.pos = new_pos
        else:
            # Пробуем движение только по X или Y
            self._try_slide_movement(dx, dy, game_state)
    
    def _calculate_new_position(self, dx: float, dy: float) -> list:
        """Рассчитывает новую позицию игрока"""
        if dx != 0 and dy != 0:
            dx *= self.speed_diagonal
            dy *= self.speed_diagonal
        else:
            dx *= self.speed
            dy *= self.speed
        return [self.pos[0] + dx, self.pos[1] + dy]
    
    def _check_collision(self, pos: list, game_state: dict) -> bool:
        """Проверяет коллизию со стенами"""
        cell_size = game_state['cell_size']
        thin_walls = game_state['thin_walls']
        
        # Проверяем углы игрока
        for x, y in self._get_corners(pos):
            cell_x, cell_y = int(x) // cell_size, int(y) // cell_size
            if is_valid_cell(cell_x, cell_y, thin_walls) and thin_walls[cell_y][cell_x] == 1:
                return True
        return False
    
    def _get_corners(self, pos: list) -> list:
        """Возвращает углы игрока для проверки коллизий"""
        return [
            (pos[0] - self.radius, pos[1] - self.radius),  # Левый верхний
            (pos[0] + self.radius, pos[1] + self.radius),  # Правый нижний
            (pos[0] - self.radius, pos[1] + self.radius),  # Левый нижний
            (pos[0] + self.radius, pos[1] - self.radius)   # Правый верхний
        ]
    
    def _try_slide_movement(self, dx: float, dy: float, game_state: dict):
        """Пытается выполнить скольжение вдоль стены"""
        # Пробуем движение только по X
        if dx != 0:
            x_pos = [self.last_valid_pos[0] + dx * self.speed, self.pos[1]]
            if not self._check_collision(x_pos, game_state):
                self.pos = x_pos
                return
        
        # Пробуем движение только по Y
        if dy != 0:
            y_pos = [self.pos[0], self.last_valid_pos[1] + dy * self.speed]
            if not self._check_collision(y_pos, game_state):
                self.pos = y_pos
    
    def update_glow(self, dt: float) -> None:
        """Обновляет свечение игрока"""
        self.glow = max(0, self.glow - dt * Config.GLOW_DECAY_RATE)