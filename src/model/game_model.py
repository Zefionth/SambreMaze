"""Модель игрового состояния"""
from src.model.player import Player
from src.model.maze import MazeGenerator
from src.model.particle import Particle
from typing import List, Tuple, Dict
import pygame
import random
import math

class GameModel:
    def __init__(self, settings: dict):
        self.settings = settings
        self.reset()
    
    def reset(self):
        self.player = Player(self.settings)
        self.thin_walls, self.maze, self.red_zones, self.cell_size = MazeGenerator.generate_maze()
        
        self.particles: List[Particle] = []
        self.white_points: List[Tuple[float, float, int]] = []
        self.red_points: List[Tuple[float, float, int]] = []
        self.red_scan_lines: List[Dict] = []
        
        self.game_won = False
        self.game_over = False
        
        self.last_white_scan_time = 0
        self.last_red_scan_time = 0
        self.left_mouse_down = False
    
    def get_wall_normal(self, cell_x: int, cell_y: int, hit_x: float, hit_y: float) -> Tuple[int, int]:
        cell_left = cell_x * self.cell_size
        cell_right = (cell_x + 1) * self.cell_size
        cell_top = cell_y * self.cell_size
        cell_bottom = (cell_y + 1) * self.cell_size
        
        dists = {
            'left': abs(hit_x - cell_left),
            'right': abs(hit_x - cell_right),
            'top': abs(hit_y - cell_top),
            'bottom': abs(hit_y - cell_bottom)
        }
        
        min_side = min(dists, key=dists.get)
        if min_side == 'left': return (1, 0)
        elif min_side == 'right': return (-1, 0)
        elif min_side == 'top': return (0, 1)
        else: return (0, -1)
    
    def precise_white_scan(self, start_pos: List[float], angle: float) -> List[Tuple[float, float, int]]:
        length = 200
        angle += random.uniform(-0.02, 0.02)
        
        closest_hit = None
        closest_dist = float('inf')
        
        for dist in range(5, length, 1):
            x = start_pos[0] + math.cos(angle) * dist
            y = start_pos[1] + math.sin(angle) * dist
            
            cell_x, cell_y = int(x)//self.cell_size, int(y)//self.cell_size
            if 0 <= cell_x < len(self.maze[0]) and 0 <= cell_y < len(self.maze):
                if self.thin_walls[cell_y][cell_x] == 1 or self.maze[cell_y][cell_x] == 2:
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_hit = (x, y, cell_x, cell_y)
                    break
        
        if closest_hit:
            x, y, cell_x, cell_y = closest_hit
            normal = self.get_wall_normal(cell_x, cell_y, x, y)
            return [(
                x + normal[0] * random.uniform(-2, 2),
                y + normal[1] * random.uniform(-2, 2),
                pygame.time.get_ticks()
            )]
        return []
    
    def add_red_scan_wave(self, start_pos: List[float], angle: float) -> Tuple[List, List]:
        length = 200
        wave_points = []
        hit_positions = []
        
        for delta in range(-45, 46, 2):
            current_angle = angle + math.radians(delta)
            for dist in range(0, length, 3):
                x = start_pos[0] + math.cos(current_angle) * dist
                y = start_pos[1] + math.sin(current_angle) * dist
                wave_points.append((x, y, pygame.time.get_ticks()))
                
                cell_x, cell_y = int(x)//self.cell_size, int(y)//self.cell_size
                if 0 <= cell_x < len(self.maze[0]) and 0 <= cell_y < len(self.maze):
                    if (cell_x, cell_y) in self.red_zones:
                        hit_positions.append((x, y))
                        break
        return wave_points, hit_positions
    
    def update(self, dt: float, mouse_pos: Tuple[int, int], keys_pressed: List[bool]):
        current_time = pygame.time.get_ticks()
        
        # Белое сканирование
        if self.left_mouse_down and current_time - self.last_white_scan_time > self.settings['white_scan_cooldown']:
            self.last_white_scan_time = current_time
            angle = math.atan2(mouse_pos[1]-self.player.pos[1], mouse_pos[0]-self.player.pos[0])
            new_points = self.precise_white_scan(self.player.pos, angle)
            
            if new_points:
                self.white_points.extend(new_points)
                self.player.glow = min(10, self.player.glow + 1)
                
                px, py, pt = new_points[0]
                part_angle = math.atan2(py - self.player.pos[1], px - self.player.pos[0])
                self.particles.append(Particle(
                    px, py, self.settings['colors']['scan'], 2, 0.4,
                    [math.cos(part_angle)*0.2, math.sin(part_angle)*0.2]
                ))
        
        # Управление игроком
        move_x = keys_pressed[pygame.K_d] - keys_pressed[pygame.K_a]
        move_y = keys_pressed[pygame.K_s] - keys_pressed[pygame.K_w]

        if move_x != 0 and move_y != 0:
            dx = move_x * self.player.speed_diagonal
            dy = move_y * self.player.speed_diagonal
        else:
            dx = move_x * self.player.speed
            dy = move_y * self.player.speed
        
        game_state = {
            'thin_walls': self.thin_walls,
            'cell_size': self.cell_size,
            'game_over': self.game_over,
            'game_won': self.game_won
        }
        self.player.update_position(dx, dy, game_state)

        # Проверка столкновений
        cell_x, cell_y = int(self.player.pos[0])//self.cell_size, int(self.player.pos[1])//self.cell_size
        if 0 <= cell_x < len(self.maze[0]) and 0 <= cell_y < len(self.maze):
            if (cell_x, cell_y) in self.red_zones and not self.game_over:
                self.game_over = True
                self.particles.append(Particle(
                    self.player.pos[0], self.player.pos[1], 
                    self.settings['colors']['danger'], 15, 2.0))
            elif self.maze[cell_y][cell_x] == 2 and not self.game_won:
                self.game_won = True
        
        # Обновление частиц и точек
        self.particles = [p for p in self.particles if p.update(dt)]
        self.player.update_glow(dt)
        
        # Удаление старых точек
        self.white_points = [(x,y,t) for x,y,t in self.white_points if current_time - t < self.settings['point_lifetime']]
        self.red_points = [(x,y,t) for x,y,t in self.red_points if current_time - t < self.settings['point_lifetime']]