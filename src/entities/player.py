"""
Модуль для работы с игроком
"""
import math
from pygame import gfxdraw
from typing import Tuple
from src.config import Config

class Player:
    def __init__(self, settings: dict):
        """
        Инициализация игрока
        
        Args:
            settings: Настройки игры (из Config)
        """
        self.pos = [Config.WIDTH // 2, Config.HEIGHT // 2]
        self.radius = settings.get('player_radius', 10)
        self.speed = settings.get('player_speed', 3.5)
        self.speed_diagonal = self.speed * 0.7071  # Скорость при диагональном движении
        self.glow = 0  # Уровень свечения
        self.color = settings['colors']['player']
    
    def update_position(self, dx: float, dy: float, game) -> None:
        """
        Обновляет позицию игрока с учетом столкновений
        
        Args:
            dx: Изменение по X
            dy: Изменение по Y
            game: Ссылка на объект игры для проверки состояния
        """
        if game.game_over or game.game_won:
            return  # Не двигаем игрока если игра завершена
        
        new_pos = self.pos.copy()
        
        if dx != 0:
            new_pos[0] += dx
            cell_x = int(new_pos[0]) // game.cell_size
            cell_y = int(self.pos[1]) // game.cell_size
            if 0 <= cell_x < len(game.thin_walls[0]) and 0 <= cell_y < len(game.thin_walls):
                if game.thin_walls[cell_y][cell_x] == 1:
                    new_pos[0] = self.pos[0]
        
        if dy != 0:
            new_pos[1] += dy
            cell_x = int(new_pos[0]) // game.cell_size
            cell_y = int(new_pos[1]) // game.cell_size
            if 0 <= cell_x < len(game.thin_walls[0]) and 0 <= cell_y < len(game.thin_walls):
                if game.thin_walls[cell_y][cell_x] == 1:
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
            cell_x, cell_y = int(x)//game.cell_size, int(y)//game.cell_size
            if 0 <= cell_x < len(game.thin_walls[0]) and 0 <= cell_y < len(game.thin_walls):
                if game.thin_walls[cell_y][cell_x] == 1:
                    can_move = False
                    break
        
        if can_move:
            self.pos = new_pos
    
    def draw(self, surface, mouse_pos: Tuple[int, int]) -> None:
        """
        Отрисовывает игрока на поверхности
        
        Args:
            surface: Поверхность для отрисовки
            mouse_pos: Позиция мыши для определения направления
        """
        angle = math.atan2(mouse_pos[1]-self.pos[1], mouse_pos[0]-self.pos[0])
        points = [
            (self.pos[0] + math.cos(angle)*self.radius*1.5,
             self.pos[1] + math.sin(angle)*self.radius*1.5),
            (self.pos[0] + math.cos(angle+2.3)*self.radius*0.8,
             self.pos[1] + math.sin(angle+2.3)*self.radius*0.8),
            (self.pos[0] + math.cos(angle-2.3)*self.radius*0.8,
             self.pos[1] + math.sin(angle-2.3)*self.radius*0.8)
        ]
        alpha = 180 + int(self.glow * 7.5)  # Увеличиваем прозрачность при свечении
        alpha = min(255, max(180, alpha))  # Ограничиваем диапазон
        gfxdraw.filled_polygon(surface, points, (*self.color, alpha))
    
    def update_glow(self, dt: float) -> None:
        """
        Обновляет уровень свечения игрока
        
        Args:
            dt: Время с последнего обновления
        """
        self.glow = max(0, self.glow - dt * 5)