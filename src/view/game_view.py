"""Визуальное представление игрового процесса"""
import pygame
import math
from pygame import gfxdraw
from typing import List, Tuple, Dict
from src.config import Config

class GameView:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont('Arial', 24)
        self.font_large = pygame.font.SysFont('Arial', 48)

    def draw(self, player, maze, thin_walls, red_zones, particles, 
            white_points, red_points, red_scan_lines, game_won, 
            game_over, colors, fog_radius, cell_size):
        """Отрисовывает текущее игровое состояние"""
        current_time = pygame.time.get_ticks()
        
        # Очистка экрана
        self.screen.fill(colors['background'])

        # Рисуем туман войны
        self.draw_fog(player.pos, fog_radius)

        # Рисуем сканированные точки
        self.draw_scan_points(white_points, red_points, current_time, colors)

        # Рисуем красные сканы
        self.draw_red_scans(red_scan_lines, current_time, colors)

        # Рисуем частицы
        for p in particles:
            p.draw(self.screen)

        # Рисуем игрока
        self.draw_player(player, pygame.mouse.get_pos(), colors)

        # Рисуем выход
        self.draw_exit(maze, cell_size, current_time, colors)

        # Наложение тумана
        self.apply_fog(player.pos, fog_radius)

        # Сообщения о победе/поражении
        self.draw_game_status(game_won, game_over, colors)

        # Кнопки интерфейса
        self.draw_ui_buttons()

        pygame.display.flip()

    def draw_fog(self, player_pos, fog_radius):
        """Создает поверхность для тумана войны"""
        self.fog_surface = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
        self.fog_surface.fill((0, 0, 0, 200))
        gfxdraw.filled_circle(self.fog_surface, int(player_pos[0]), int(player_pos[1]), 
                            fog_radius, (0, 0, 0, 0))

    def draw_scan_points(self, white_points, red_points, current_time, colors):
        """Отрисовывает точки сканирования"""
        for x, y, t in white_points:
            age = (current_time - t) / 2500
            alpha = int(255 * (1 - age))
            pulse = math.sin(current_time/200) * 1.5
            radius = int(3 + pulse)
            gfxdraw.filled_circle(self.screen, int(x), int(y), radius, 
                                (*colors['scan'], alpha))

        for x, y, t in red_points:
            age = (current_time - t) / 2500
            alpha = int(220 * (1 - age))
            pulse = math.sin(current_time/200) * 2
            radius = int(1 + pulse)
            gfxdraw.filled_circle(self.screen, int(x), int(y), radius, 
                                (*colors['danger'], alpha))

    def draw_red_scans(self, red_scan_lines, current_time, colors):
        """Отрисовывает эффекты красного сканирования"""
        for scan in red_scan_lines:
            if current_time - scan['start_time'] < scan['duration']:
                # Отрисовка границ скана
                for point in scan['left_bound'] + scan['right_bound']:
                    x, y, t = point
                    alpha = int(150 * (1 - (current_time - t)/scan['duration']))
                    gfxdraw.filled_circle(self.screen, int(x), int(y), 1, 
                                        (*colors['red_scan'], alpha))

                # Отрисовка линий между точками
                for bound in [scan['left_bound'], scan['right_bound']]:
                    for i in range(len(bound) - 1):
                        x1, y1, t1 = bound[i]
                        x2, y2, t2 = bound[i+1]
                        alpha = int(80 * (1 - (current_time - t1)/scan['duration']))
                        pygame.draw.line(self.screen, (*colors['red_scan'], alpha), 
                                       (x1, y1), (x2, y2), 1)

    def draw_player(self, player, mouse_pos, colors):
        """Отрисовывает игрока"""
        angle = math.atan2(mouse_pos[1]-player.pos[1], mouse_pos[0]-player.pos[0])
        points = [
            (player.pos[0] + math.cos(angle)*player.radius*1.5,
             player.pos[1] + math.sin(angle)*player.radius*1.5),
            (player.pos[0] + math.cos(angle+2.3)*player.radius*0.8,
             player.pos[1] + math.sin(angle+2.3)*player.radius*0.8),
            (player.pos[0] + math.cos(angle-2.3)*player.radius*0.8,
             player.pos[1] + math.sin(angle-2.3)*player.radius*0.8)
        ]
        alpha = 180 + int(player.glow * 7.5)
        alpha = min(255, max(180, alpha))
        gfxdraw.filled_polygon(self.screen, points, (*colors['player'], alpha))

    def draw_exit(self, maze, cell_size, current_time, colors):
        """Отрисовывает выход из лабиринта"""
        for y in range(len(maze)):
            for x in range(len(maze[0])):
                if maze[y][x] == 2:
                    exit_rect = pygame.Rect(x*cell_size, y*cell_size, 
                                          cell_size, cell_size)
                    pygame.draw.rect(self.screen, colors['exit'], exit_rect)
                    pulse = math.sin(current_time/500) * 3
                    pygame.draw.rect(self.screen, (*colors['exit'], 50), 
                                   exit_rect.inflate(pulse*2, pulse*2))

    def apply_fog(self, player_pos, fog_radius):
        """Накладывает туман войны"""
        self.screen.blit(self.fog_surface, (0, 0))

    def draw_game_status(self, game_won, game_over, colors):
        """Отрисовывает сообщения о победе/поражении"""
        if game_won:
            text = self.font_large.render("YOU ESCAPED!", True, colors['exit'])
            self.screen.blit(text, (Config.WIDTH//2-text.get_width()//2, 
                                  Config.HEIGHT//2-text.get_height()//2))
        elif game_over:
            text = self.font_large.render("GAME OVER", True, colors['danger'])
            self.screen.blit(text, (Config.WIDTH//2-text.get_width()//2, 
                                  Config.HEIGHT//2-text.get_height()//2))

    def draw_ui_buttons(self):
        """Отрисовывает кнопки интерфейса"""
        # Кнопка Restart
        restart_rect = pygame.Rect(10, 10, 100, 30)
        pygame.draw.rect(self.screen, Config.WHITE, restart_rect)
        text = self.font.render("Restart", True, Config.BLACK)
        self.screen.blit(text, (restart_rect.centerx-text.get_width()//2, 
                          restart_rect.centery-text.get_height()//2))

        # Кнопка Menu
        menu_rect = pygame.Rect(120, 10, 100, 30)
        pygame.draw.rect(self.screen, Config.WHITE, menu_rect)
        text = self.font.render("Menu", True, Config.BLACK)
        self.screen.blit(text, (menu_rect.centerx-text.get_width()//2, 
                          menu_rect.centery-text.get_height()//2))