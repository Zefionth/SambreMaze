"""Модель игрока.

Этот модуль содержит класс Player, который реализует логику управления игроком,
включая движение, коллизии и визуальные эффекты.
"""

from src.config import Config
from src.utils import is_valid_cell
from typing import Dict, List, Any


class Player:
    """Класс, представляющий игрока в игре.
    
    Отвечает за:
    - Хранение и обновление позиции игрока
    - Обработку движения и коллизий
    - Управление визуальным свечением
    - Взаимодействие с игровым миром
    
    Attributes:
        pos (List[float]): Текущая позиция игрока [x, y]
        radius (float): Радиус игрока
        speed (float): Базовая скорость движения
        speed_diagonal (float): Скорость движения по диагонали
        glow (float): Уровень свечения игрока (для визуальных эффектов)
        color (Tuple[int, int, int]): Цвет игрока (RGB)
        last_valid_pos (List[float]): Последняя валидная позиция без коллизий
    """
    
    def __init__(self, settings: Dict[str, Any]) -> None:
        """Инициализирует игрока с заданными настройками.
        
        Args:
            settings: Словарь настроек игры
        """
        self.pos = [Config.WIDTH // 2, Config.HEIGHT // 2]
        self.radius = settings.get(
            'player_radius', 
            Config.DEFAULT_SETTINGS['player_radius']
        )
        self.speed = settings.get(
            'player_speed', 
            Config.DEFAULT_SETTINGS['player_speed']
        )
        self.speed_diagonal = self.speed * Config.DIAGONAL_FACTOR
        self.glow = 0.0
        self.color = settings['colors']['player']
        self.last_valid_pos = self.pos.copy()
    
    def update_position(
        self, 
        dx: float, 
        dy: float, 
        game_state: Dict[str, Any]
    ) -> None:
        """Обновляет позицию игрока с учетом коллизий.
        
        Args:
            dx: Изменение позиции по оси X (-1, 0, 1)
            dy: Изменение позиции по оси Y (-1, 0, 1)
            game_state: Текущее состояние игры
        """
        if game_state['game_over'] or game_state['game_won']:
            return
        
        # последняя валидная позиция
        self.last_valid_pos = self.pos.copy()
        
        # рассчет новой позиции
        new_pos = self._calculate_new_position(dx, dy)
        
        # проверка коллизии и обновление позиции
        if not self._check_collision(new_pos, game_state):
            self.pos = new_pos
        else:
            self._try_slide_movement(dx, dy, game_state)
    
    def _calculate_new_position(self, dx: float, dy: float) -> List[float]:
        """Рассчитывает новую позицию игрока на основе входных данных.
        
        Args:
            dx: Направление по X (-1 влево, 1 вправо)
            dy: Направление по Y (-1 вверх, 1 вниз)
            
        Returns:
            List[float]: Новая позиция [x, y]
        """
        # рассчет смещения с учетом диагонального движения
        if dx != 0 and dy != 0:
            actual_dx = dx * self.speed_diagonal
            actual_dy = dy * self.speed_diagonal
        else:
            actual_dx = dx * self.speed
            actual_dy = dy * self.speed
            
        return [self.pos[0] + actual_dx, self.pos[1] + actual_dy]
    
    def _check_collision(
        self, 
        pos: List[float], 
        game_state: Dict[str, Any]
    ) -> bool:
        """Проверяет коллизию со стенами в заданной позиции.
        
        Args:
            pos: Позиция для проверки [x, y]
            game_state: Текущее состояние игры
            
        Returns:
            bool: True если есть коллизия, иначе False
        """
        cell_size = game_state['cell_size']
        thin_walls = game_state['thin_walls']
        
        # ячейка, в которой находится игрок
        cell_x = int(pos[0] // cell_size)
        cell_y = int(pos[1] // cell_size)
        
        # проверка коллизии с тонкими стенами
        if is_valid_cell(cell_x, cell_y, thin_walls):
            return thin_walls[cell_y][cell_x] == 1
            
        return False

    def _try_slide_movement(
        self, 
        dx: float, 
        dy: float, 
        game_state: Dict[str, Any]
    ) -> None:
        """Пытается выполнить движение вдоль стены при коллизии.
        
        Args:
            dx: Направление по X (-1, 0, 1)
            dy: Направление по Y (-1, 0, 1)
            game_state: Текущее состояние игры
        """
        # только по X
        if dx != 0:
            x_pos = [self.last_valid_pos[0] + dx * self.speed, self.pos[1]]
            if not self._check_collision(x_pos, game_state):
                self.pos = x_pos
                return
        
        # только по Y
        if dy != 0:
            y_pos = [self.pos[0], self.last_valid_pos[1] + dy * self.speed]
            if not self._check_collision(y_pos, game_state):
                self.pos = y_pos
    
    def update_glow(self, dt: float) -> None:
        """Обновляет уровень свечения игрока.
        
        Свечение постепенно уменьшается со временем.
        
        Args:
            dt: Время, прошедшее с предыдущего обновления (в секундах)
        """
        self.glow = max(0.0, self.glow - dt * Config.GLOW_DECAY_RATE)