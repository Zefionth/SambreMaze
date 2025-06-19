"""Модель игрового состояния"""
from src.model.player import Player
from src.model.maze import MazeGenerator
from src.model.particle import Particle
from src.utils import is_valid_cell
from src.config import Config
from typing import List, Tuple, Dict
import pygame
import math
import random
import heapq

class GameModel:
    """Класс, управляющий состоянием игры, включая игрока, лабиринт и игровые события."""
    
    def __init__(self, settings: dict):
        self.settings = settings
        self.reset()
        self.show_path = False
        self.path = []
    
    def reset(self):
        """Сбрасывает игровое состояние к начальным значениям."""
        self.player = Player(self.settings)
        self.thin_walls, self.maze, self.danger_zones, self.cell_size = MazeGenerator.generate_maze()
        
        self.particles: List[Particle] = []
        self.locator_points: List[Tuple[float, float, int]] = []
        self.detector_points: List[Tuple[float, float, int]] = []
        self.detector_lines: List[Dict] = []
        
        self.game_won = False
        self.game_over = False
        
        self.last_locator_time = 0
        self.last_detector_time = 0
        self.left_mouse_down = False
        
        self.show_path = False
        self.path = []
    
    def update(self, dt: float, mouse_pos: Tuple[int, int], keys_pressed: List[bool]):
        """Обновляет игровое состояние."""
        current_time = pygame.time.get_ticks()

        self._handle_locator_scan(current_time, mouse_pos)
        self._handle_player_movement(keys_pressed)
        self._check_game_status()
        self._update_particles_and_points(dt, current_time)

    def _handle_locator_scan(self, current_time: int, mouse_pos: Tuple[int, int]):
        """Обрабатывает сканирование локатором."""
        if self.left_mouse_down and current_time - self.last_locator_time > self.settings['locator_cooldown']:
            self.last_locator_time = current_time
            angle = math.atan2(mouse_pos[1]-self.player.pos[1], mouse_pos[0]-self.player.pos[0])
            new_points = self.precise_locator_scan(self.player.pos, angle)
            
            if new_points:
                self.locator_points.extend(new_points)
                self.player.glow = min(Config.MAX_GLOW, self.player.glow + Config.GLOW_INCREASE)
                
                px, py, pt = new_points[0]
                part_angle = math.atan2(py - self.player.pos[1], px - self.player.pos[0])
                self.particles.append(Particle(
                    px, py, self.settings['colors']['locator'], 
                    Config.PARTICLE_SIZE, Config.PARTICLE_LIFETIME,
                    [math.cos(part_angle)*Config.PARTICLE_SPEED, math.sin(part_angle)*Config.PARTICLE_SPEED]
                ))

    def _handle_player_movement(self, keys_pressed: List[bool]):
        """Обрабатывает движение игрока."""
        move_x = keys_pressed[pygame.K_d] - keys_pressed[pygame.K_a]
        move_y = keys_pressed[pygame.K_s] - keys_pressed[pygame.K_w]
        
        game_state = {
            'thin_walls': self.thin_walls,
            'cell_size': self.cell_size,
            'game_over': self.game_over,
            'game_won': self.game_won
        }
        
        self.player.update_position(move_x, move_y, game_state)

    def _check_game_status(self):
        """Проверяет условия победы или поражения (по центральной точке)"""
        cell_x = int(self.player.pos[0] // self.cell_size)
        cell_y = int(self.player.pos[1] // self.cell_size)
        
        if is_valid_cell(cell_x, cell_y, self.maze):
            if (cell_x, cell_y) in self.danger_zones and not self.game_over:
                self._trigger_game_over()
            elif self.maze[cell_y][cell_x] == 2 and not self.game_won:
                self.game_won = True
    
    def _trigger_game_over(self):
        """Активирует состояние поражения с визуальными эффектами"""
        self.game_over = True
        
        self.particles.append(Particle(
            self.player.pos[0], self.player.pos[1], 
            Config.RED,
            Config.GAMEOVER_PARTICLE_SIZE, 
            Config.GAMEOVER_PARTICLE_LIFETIME
        ))

    def _update_particles_and_points(self, dt: float, current_time: int):
        """Обновляет состояние частиц и временных точек."""
        self.particles = [p for p in self.particles if p.update(dt)]
        self.player.update_glow(dt)
        
        # Удаление старых точек
        self.locator_points = [(x,y,t) for x,y,t in self.locator_points 
                            if current_time - t < self.settings['point_lifetime']]
        self.detector_points = [(x,y,t) for x,y,t in self.detector_points 
                            if current_time - t < self.settings['point_lifetime']]

    def precise_locator_scan(self, start_pos: List[float], angle: float) -> List[Tuple[float, float, int]]:
        """Выполняет точное сканирование локатором в заданном направлении."""
        length = Config.LOCATOR_SCAN_LENGTH
        angle += random.uniform(-Config.LOCATOR_ANGLE_VARIATION, Config.LOCATOR_ANGLE_VARIATION)
        
        closest_hit = None
        closest_dist = float('inf')
        
        for dist in range(5, length, Config.LOCATOR_SCAN_STEP):
            x = start_pos[0] + math.cos(angle) * dist
            y = start_pos[1] + math.sin(angle) * dist
            
            cell_x, cell_y = int(x)//self.cell_size, int(y)//self.cell_size
            if is_valid_cell(cell_x, cell_y, self.thin_walls):
                if self.thin_walls[cell_y][cell_x] == 1 or self.maze[cell_y][cell_x] == 2:
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_hit = (x, y, cell_x, cell_y)
                    break
        
        if closest_hit:
            x, y, cell_x, cell_y = closest_hit
            normal = self.get_wall_normal(cell_x, cell_y, x, y)
            return [(x + normal[0] * random.uniform(-Config.LOCATOR_HIT_VARIATION, Config.LOCATOR_HIT_VARIATION),
                    y + normal[1] * random.uniform(-Config.LOCATOR_HIT_VARIATION, Config.LOCATOR_HIT_VARIATION),
                    pygame.time.get_ticks())]
        return []
    
    def get_wall_normal(self, cell_x: int, cell_y: int, hit_x: float, hit_y: float) -> Tuple[int, int]:
        """Определяет нормаль стены в точке столкновения."""
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
    
    def add_detector_wave(self, start_pos: List[float], angle: float) -> Tuple[List, List]:
        """Создает волну детектора в заданном направлении."""
        wave_points = []
        hit_positions = []
        
        for delta in range(Config.DETECTOR_ANGLE_MIN, Config.DETECTOR_ANGLE_MAX, Config.DETECTOR_ANGLE_STEP):
            current_angle = angle + math.radians(delta)
            for dist in range(0, Config.DETECTOR_SCAN_LENGTH, Config.DETECTOR_SCAN_STEP):
                x = start_pos[0] + math.cos(current_angle) * dist
                y = start_pos[1] + math.sin(current_angle) * dist
                wave_points.append((x, y, pygame.time.get_ticks()))
                
                cell_x, cell_y = int(x)//self.cell_size, int(y)//self.cell_size
                if is_valid_cell(cell_x, cell_y, self.maze):
                    if (cell_x, cell_y) in self.danger_zones:
                        hit_positions.append((x, y))
                        break
        return wave_points, hit_positions

    def find_path_to_exit(self):
        """Находит путь к выходу из лабиринта с использованием алгоритма A*."""
        start_x = int(self.player.pos[0] // self.cell_size)
        start_y = int(self.player.pos[1] // self.cell_size)
        
        exit_pos = self._find_exit_position()
        if not exit_pos:
            return

        self._run_a_star_algorithm(start_x, start_y, exit_pos)

    def _find_exit_position(self) -> Tuple[int, int]:
        """Находит позицию выхода в лабиринте."""
        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                if self.maze[y][x] == 2:
                    return (x, y)
        return None

    def _run_a_star_algorithm(self, start_x: int, start_y: int, exit_pos: Tuple[int, int]):
        """Выполняет алгоритм A* для поиска пути."""
        open_set = []
        heapq.heappush(open_set, (0, (start_x, start_y)))
        came_from = {}
        g_score = {(start_x, start_y): 0}
        f_score = {(start_x, start_y): self.heuristic((start_x, start_y), exit_pos)}

        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == exit_pos:
                self.reconstruct_path(came_from, current)
                return

            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                if self._is_valid_neighbor(neighbor):
                    self._process_neighbor(current, neighbor, g_score, f_score, came_from, exit_pos, open_set)

    def _is_valid_neighbor(self, neighbor: Tuple[int, int]) -> bool:
        """Проверяет, является ли соседняя клетка проходимой."""
        return (is_valid_cell(neighbor[0], neighbor[1], self.maze) and 
                self.maze[neighbor[1]][neighbor[0]] != 1)

    def _process_neighbor(self, current: Tuple[int, int], neighbor: Tuple[int, int],
                         g_score: Dict, f_score: Dict, came_from: Dict,
                         exit_pos: Tuple[int, int], open_set: List):
        """Обрабатывает соседнюю клетку в алгоритме A*."""
        tentative_g_score = g_score[current] + 1
        
        if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
            came_from[neighbor] = current
            g_score[neighbor] = tentative_g_score
            f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, exit_pos)
            heapq.heappush(open_set, (f_score[neighbor], neighbor))

    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Вычисляет манхэттенское расстояние между точками."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def reconstruct_path(self, came_from: Dict, current: Tuple[int, int]):
        """Восстанавливает путь от текущей позиции до старта."""
        self.path = []
        while current in came_from:
            self.path.append(current)
            current = came_from[current]
        self.path.reverse()