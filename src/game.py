"""Основной класс игры"""
import pygame
import math
import random
from pygame import gfxdraw
from typing import List, Tuple, Dict
from src.config import Config
from src.entities.particle import Particle
from src.entities.player import Player
from src.maze.generator import MazeGenerator
from src.menu.menu import Menu

class ScannerGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption("Scanner Sombre: Invisible Walls")
        
        self.font = pygame.font.SysFont('Arial', 24)
        self.font_large = pygame.font.SysFont('Arial', 48)
        
        self.settings = Config.load_settings()
        self.apply_settings(self.settings)
        
        self.menu = Menu(self)
        self.game_active = False
    
    def apply_settings(self, settings: Dict) -> None:
        default = Config.DEFAULT_SETTINGS
        
        # Инициализация игрока с настройками
        self.player = Player(settings)
        
        # Параметры игры
        self.fog_radius = settings.get('fog_radius', default['fog_radius'])
        self.point_lifetime = settings.get('point_lifetime', default['point_lifetime'])
        self.white_scan_cooldown = settings.get('white_scan_cooldown', default['white_scan_cooldown'])
        self.red_scan_cooldown = settings.get('red_scan_cooldown', default['red_scan_cooldown'])
        
        colors = settings.get('colors', default['colors'])
        self.colors = {
            'background': colors.get('background', default['colors']['background']),
            'walls': colors.get('walls', default['colors']['walls']),
            'exit': colors.get('exit', default['colors']['exit']),
            'danger': colors.get('danger', default['colors']['danger']),
            'scan': colors.get('scan', default['colors']['scan']),
            'red_scan': colors.get('red_scan', default['colors']['red_scan'])
        }
    
    def start_game(self) -> None:
        self.reset_game()
        self.game_active = True
    
    def reset_game(self) -> None:
        # Сброс состояния игрока
        self.player.pos = [Config.WIDTH // 2, Config.HEIGHT // 2]
        self.player.glow = 0
        
        # Эффекты и точки
        self.particles = []
        self.white_points = []
        self.red_points = []
        self.red_scan_lines = []
        
        # Состояние игры
        self.game_won = False
        self.game_over = False
        
        # Время сканирования
        self.last_white_scan_time = 0
        self.last_red_scan_time = 0
        self.left_mouse_down = False
        
        # Генерация лабиринта
        self.thin_walls, self.maze, self.red_zones, self.cell_size, _ = MazeGenerator.generate_maze()
        self.wall_surface = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
    
    def get_wall_normal(self, cell_x: int, cell_y: int, 
                       hit_x: float, hit_y: float) -> Tuple[int, int]:
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
    
    def precise_white_scan(self, start_pos: List[float], 
                          angle: float) -> List[Tuple[float, float, int]]:
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
    
    def add_red_scan_wave(self, start_pos: List[float], 
                         angle: float) -> Tuple[List, List]:
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
    
    def handle_events(self) -> bool:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.left_mouse_down = True
                elif event.button == 3 and current_time - self.last_red_scan_time > self.red_scan_cooldown:
                    self.last_red_scan_time = current_time
                    angle = math.atan2(mouse_pos[1]-self.player.pos[1], mouse_pos[0]-self.player.pos[0])
                    wave_points, hit_positions = self.add_red_scan_wave(self.player.pos, angle)
                    
                    left_bound = []
                    right_bound = []
                    for dist in range(0, self.fog_radius, 3):
                        lx = self.player.pos[0] + math.cos(angle - math.radians(45)) * dist
                        ly = self.player.pos[1] + math.sin(angle - math.radians(45)) * dist
                        left_bound.append((lx, ly, current_time))
                        
                        rx = self.player.pos[0] + math.cos(angle + math.radians(45)) * dist
                        ry = self.player.pos[1] + math.sin(angle + math.radians(45)) * dist
                        right_bound.append((rx, ry, current_time))
                    
                    self.red_scan_lines.append({
                        'points': wave_points,
                        'left_bound': left_bound,
                        'right_bound': right_bound,
                        'start_time': current_time,
                        'duration': 500,
                        'hit_positions': hit_positions,
                        'hit_revealed': [False]*len(hit_positions)
                    })
                    
                    for pos in hit_positions:
                        self.red_points.append((*pos, current_time))
                        self.particles.append(Particle(pos[0], pos[1], self.colors['danger'], 2, 1.0))
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.left_mouse_down = False
        
        return True
    
    def update(self, dt: float) -> None:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        
        # Проверка состояния игры перед обновлением
        if not self.game_over and not self.game_won:
            # Белое сканирование
            if self.left_mouse_down and current_time - self.last_white_scan_time > self.white_scan_cooldown:
                self.last_white_scan_time = current_time
                angle = math.atan2(mouse_pos[1]-self.player.pos[1], mouse_pos[0]-self.player.pos[0])
                new_points = self.precise_white_scan(self.player.pos, angle)
                
                if new_points:
                    self.white_points.extend(new_points)
                    self.player.glow = min(10, self.player.glow + 1)
                    
                    px, py, pt = new_points[0]
                    part_angle = math.atan2(py - self.player.pos[1], px - self.player.pos[0])
                    self.particles.append(Particle(
                        px, py, self.colors['scan'], 2, 0.4,
                        [math.cos(part_angle)*0.2, math.sin(part_angle)*0.2]
                    ))
            
            # Управление игроком (только если игра не завершена)
            keys = pygame.key.get_pressed()
            move_x = keys[pygame.K_d] - keys[pygame.K_a]
            move_y = keys[pygame.K_s] - keys[pygame.K_w]

            # Вычисление скорости движения
            if move_x != 0 and move_y != 0:
                dx = move_x * self.player.speed_diagonal
                dy = move_y * self.player.speed_diagonal
            else:
                dx = move_x * self.player.speed
                dy = move_y * self.player.speed
            
            # Обновление позиции игрока
            self.player.update_position(dx, dy, self)

        # Проверка столкновений с опасными зонами и выходом
        cell_x, cell_y = int(self.player.pos[0])//self.cell_size, int(self.player.pos[1])//self.cell_size
        if 0 <= cell_x < len(self.maze[0]) and 0 <= cell_y < len(self.maze):
            if (cell_x, cell_y) in self.red_zones and not self.game_over:
                self.game_over = True
                self.particles.append(Particle(
                    self.player.pos[0], self.player.pos[1], 
                    self.colors['danger'], 15, 2.0))
            elif self.maze[cell_y][cell_x] == 2 and not self.game_won:
                self.game_won = True
        
        # Обновление частиц и точек
        self.particles = [p for p in self.particles if p.update(dt)]
        self.player.update_glow(dt)
        
        # Удаление старых точек
        self.white_points = [(x,y,t) for x,y,t in self.white_points if current_time - t < self.point_lifetime]
        self.red_points = [(x,y,t) for x,y,t in self.red_points if current_time - t < self.point_lifetime]
    
    def draw(self) -> None:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        
        # Очистка экрана
        self.screen.fill(self.colors['background'])
        
        # Создание тумана войны
        fog = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
        fog.fill((0, 0, 0, 200))
        gfxdraw.filled_circle(fog, int(self.player.pos[0]), int(self.player.pos[1]), 
                            self.fog_radius, (0,0,0,0))
        
        # Стены (невидимые)
        self.screen.blit(self.wall_surface, (0, 0))
        
        # Белые точки сканирования
        for x, y, t in self.white_points:
            age = (current_time - t) / self.point_lifetime
            alpha = int(255 * (1 - age))
            pulse = math.sin(current_time/200) * 1.5
            radius = int(3 + pulse)
            gfxdraw.filled_circle(self.screen, int(x), int(y), radius, 
                                (*self.colors['scan'], alpha))
        
        # Красные точки сканирования
        for x, y, t in self.red_points:
            age = (current_time - t) / self.point_lifetime
            alpha = int(220 * (1 - age))
            pulse = math.sin(current_time/200) * 2
            radius = int(1 + pulse)
            gfxdraw.filled_circle(self.screen, int(x), int(y), radius, 
                                (*self.colors['danger'], alpha))
        
        # Красные линии сканирования
        for scan in self.red_scan_lines:
            if current_time - scan['start_time'] < scan['duration']:
                # Левая граница
                for point in scan['left_bound']:
                    x, y, t = point
                    alpha = int(150 * (1 - (current_time - t)/scan['duration']))
                    gfxdraw.filled_circle(self.screen, int(x), int(y), 1, 
                                        (*self.colors['red_scan'], alpha))
                
                # Правая граница
                for point in scan['right_bound']:
                    x, y, t = point
                    alpha = int(150 * (1 - (current_time - t)/scan['duration']))
                    gfxdraw.filled_circle(self.screen, int(x), int(y), 1, 
                                        (*self.colors['red_scan'], alpha))

                # Соединение точек
                for i in range(len(scan['left_bound']) - 1):
                    x1, y1, t1 = scan['left_bound'][i]
                    x2, y2, t2 = scan['left_bound'][i+1]
                    alpha = int(80 * (1 - (current_time - t1)/scan['duration']))
                    pygame.draw.line(self.screen, (*self.colors['red_scan'], alpha), 
                                   (x1, y1), (x2, y2), 1)
                
                for i in range(len(scan['right_bound']) - 1):
                    x1, y1, t1 = scan['right_bound'][i]
                    x2, y2, t2 = scan['right_bound'][i+1]
                    alpha = int(80 * (1 - (current_time - t1)/scan['duration']))
                    pygame.draw.line(self.screen, (*self.colors['red_scan'], alpha), 
                                   (x1, y1), (x2, y2), 1)
        
        # Отрисовка частиц
        for p in self.particles:
            p.draw(self.screen)
        
        # Отрисовка игрока
        self.player.draw(self.screen, mouse_pos)
        
        # Отрисовка выхода
        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                if self.maze[y][x] == 2:
                    exit_rect = pygame.Rect(x*self.cell_size, y*self.cell_size, 
                                          self.cell_size, self.cell_size)
                    pygame.draw.rect(self.screen, self.colors['exit'], exit_rect)
                    pulse = math.sin(current_time/500) * 3
                    pygame.draw.rect(self.screen, (*self.colors['exit'], 50), 
                                   exit_rect.inflate(pulse*2, pulse*2))
        
        # Наложение тумана
        self.screen.blit(fog, (0, 0))
        
        # Сообщения о победе/поражении
        if self.game_won:
            text = self.font_large.render("YOU ESCAPED!", True, self.colors['exit'])
            self.screen.blit(text, (Config.WIDTH//2-text.get_width()//2, 
                                  Config.HEIGHT//2-text.get_height()//2))
        elif self.game_over:
            text = self.font_large.render("GAME OVER", True, self.colors['danger'])
            self.screen.blit(text, (Config.WIDTH//2-text.get_width()//2, 
                                  Config.HEIGHT//2-text.get_height()//2))
        
        # Кнопки управления
        restart_rect = pygame.Rect(10, 10, 100, 30)
        pygame.draw.rect(self.screen, Config.WHITE, restart_rect)
        text = self.font.render("Restart", True, Config.BLACK)
        self.screen.blit(text, (restart_rect.centerx-text.get_width()//2, 
                          restart_rect.centery-text.get_height()//2))
        
        menu_rect = pygame.Rect(120, 10, 100, 30)
        pygame.draw.rect(self.screen, Config.WHITE, menu_rect)
        text = self.font.render("Menu", True, Config.BLACK)
        self.screen.blit(text, (menu_rect.centerx-text.get_width()//2, 
                          menu_rect.centery-text.get_height()//2))
        
        # Обработка нажатий кнопок
        if pygame.mouse.get_pressed()[0]:
            if restart_rect.collidepoint(pygame.mouse.get_pos()):
                self.reset_game()
            elif menu_rect.collidepoint(pygame.mouse.get_pos()):
                self.game_active = False
        
        pygame.display.flip()
    
    def run(self) -> None:
        """Главный игровой цикл"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            dt = clock.tick(60) / 1000.0  # Delta time в секундах
            
            if self.game_active:
                running = self.handle_events()
                self.update(dt)
                self.draw()
            else:
                running = self.menu.handle_events()
                self.menu.draw(self.screen)
        
        pygame.quit()