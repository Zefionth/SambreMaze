"""Визуальное представление игрового процесса"""
import pygame
import math
from pygame import gfxdraw
from src.config import Config

class GameView:
    def __init__(self, screen):
        self.screen = screen
        self._init_fonts()
        self._init_surfaces()
        
    def _init_fonts(self):
        """Инициализация шрифтов"""
        self.font = pygame.font.SysFont('Arial', 24)
        self.font_large = pygame.font.SysFont('Arial', 48)
        
    def _init_surfaces(self):
        """Инициализация поверхностей для эффектов"""
        self.fog_surface = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
        self.pulse_time = 0
        
    def draw(self, game_state):
        """Основной метод отрисовки игрового состояния"""
        self._clear_screen(game_state['colors']['background'])
        self._draw_game_world(game_state)
        self._draw_ui(game_state)
        pygame.display.flip()
        self.pulse_time += 0.1
        
    def _clear_screen(self, bg_color):
        """Очистка экрана с заданным цветом"""
        self.screen.fill(self._normalize_color(bg_color))
        
    def _draw_game_world(self, game_state):
        """Отрисовка игрового мира"""
        if game_state['show_path']:
            self._draw_path(game_state['path'], game_state['cell_size'], game_state['colors']['exit'])
            
        self._create_fog(game_state['player'].pos, game_state['fog_radius'])
        self._draw_particles(game_state['particles'])
        self._draw_player(game_state['player'], game_state['colors']['player'])
        self._draw_exit(game_state['maze'], game_state['cell_size'], game_state['colors']['exit'])
        self._draw_points(game_state['locator_points'], game_state['colors']['locator'], 1.5, 3)
        self._draw_points(game_state['detector_points'], game_state['colors']['danger'], 2.0, 1)
        self._draw_detector_waves(game_state['detector_lines'], game_state['colors']['detector'])
        
        if self.fog_surface:
            self.screen.blit(self.fog_surface, (0, 0))
            
    def _draw_ui(self, game_state):
        """Отрисовка интерфейса пользователя"""
        self._draw_game_status(game_state['game_won'], game_state['game_over'], game_state['colors'])
        self._draw_ui_buttons()
        
    def _normalize_color(self, color, alpha=255):
        """Приведение цвета к единому формату (R, G, B, A)"""
        if isinstance(color, list):
            color = tuple(color)
        return color if len(color) == 4 else (*color[:3], alpha)
        
    def _create_fog(self, player_pos, fog_radius):
        """Создание эффекта тумана войны"""
        self.fog_surface.fill((0, 0, 0, 200))
        gfxdraw.filled_circle(
            self.fog_surface, 
            int(player_pos[0]), 
            int(player_pos[1]), 
            fog_radius, 
            (0, 0, 0, 0)
        )
        
    def _draw_path(self, path, cell_size, color):
        """Отрисовка пути к выходу"""
        if not path:
            return
            
        for i in range(len(path) - 1):
            start = (
                path[i][0] * cell_size + cell_size // 2,
                path[i][1] * cell_size + cell_size // 2
            )
            end = (
                path[i+1][0] * cell_size + cell_size // 2,
                path[i+1][1] * cell_size + cell_size // 2
            )
            pygame.draw.line(
                self.screen, 
                self._normalize_color(color), 
                start, 
                end, 
                3
            )
            
    def _draw_points(self, points, base_color, pulse_factor, base_radius):
        """Отрисовка точек с эффектом пульсации"""
        current_time = pygame.time.get_ticks()
        
        for point in points:
            x, y, t = point
            age = (current_time - t) / 2500  # Время жизни точек
            
            if age >= 1.0:
                continue
                
            alpha = int(255 * (1 - age))
            pulse = math.sin(self.pulse_time) * pulse_factor
            radius = int(base_radius + pulse)
            color = self._normalize_color(base_color, alpha)
            
            self._draw_circle(x, y, radius, color)
            
    def _draw_circle(self, x, y, radius, color):
        """Универсальный метод отрисовки круга"""
        try:
            gfxdraw.filled_circle(
                self.screen, 
                int(x), 
                int(y), 
                radius, 
                color
            )
        except:
            pygame.draw.circle(
                self.screen, 
                color[:3], 
                (int(x), int(y)), 
                radius
            )
            
    def _draw_particles(self, particles):
        """Отрисовка частиц"""
        for p in particles:
            p.draw(self.screen)
            
    def _draw_player(self, player, base_color):
        """Отрисовка игрока"""
        mouse_pos = pygame.mouse.get_pos()
        angle = math.atan2(
            mouse_pos[1] - player.pos[1], 
            mouse_pos[0] - player.pos[0]
        )
        
        points = [
            (
                player.pos[0] + math.cos(angle) * player.radius * 1.5,
                player.pos[1] + math.sin(angle) * player.radius * 1.5
            ),
            (
                player.pos[0] + math.cos(angle + 2.3) * player.radius * 0.8,
                player.pos[1] + math.sin(angle + 2.3) * player.radius * 0.8
            ),
            (
                player.pos[0] + math.cos(angle - 2.3) * player.radius * 0.8,
                player.pos[1] + math.sin(angle - 2.3) * player.radius * 0.8
            )
        ]
        
        alpha = 180 + int(player.glow * 7.5)
        alpha = min(255, max(180, alpha))
        color = self._normalize_color(base_color, alpha)
        
        try:
            gfxdraw.filled_polygon(self.screen, points, color)
        except:
            pygame.draw.polygon(self.screen, color[:3], points)
            
    def _draw_exit(self, maze, cell_size, base_color):
        """Отрисовка выхода из лабиринта"""
        for y in range(len(maze)):
            for x in range(len(maze[0])):
                if maze[y][x] == 2:
                    exit_rect = pygame.Rect(
                        x * cell_size, 
                        y * cell_size, 
                        cell_size, 
                        cell_size
                    )
                    
                    pygame.draw.rect(
                        self.screen, 
                        self._normalize_color(base_color), 
                        exit_rect
                    )
                    
                    pulse = math.sin(self.pulse_time) * 3
                    pygame.draw.rect(
                        self.screen, 
                        self._normalize_color(base_color, 50), 
                        exit_rect.inflate(pulse * 2, pulse * 2)
                    )
                    
    def _draw_detector_waves(self, waves, base_color):
        """Отрисовка волн детектора"""
        current_time = pygame.time.get_ticks()
        
        for wave in waves:
            if current_time - wave['start_time'] < wave['duration']:
                self._draw_wave_points(wave, base_color, current_time)
                self._draw_wave_lines(wave, base_color, current_time)
                
    def _draw_wave_points(self, wave, base_color, current_time):
        """Отрисовка точек волны"""
        for point in wave['left_bound'] + wave['right_bound']:
            x, y, t = point
            alpha = int(150 * (1 - (current_time - t) / wave['duration']))
            color = self._normalize_color(base_color, alpha)
            self._draw_circle(x, y, 1, color)
            
    def _draw_wave_lines(self, wave, base_color, current_time):
        """Отрисовка линий волны"""
        for bound in [wave['left_bound'], wave['right_bound']]:
            for i in range(len(bound) - 1):
                x1, y1, t1 = bound[i]
                x2, y2, t2 = bound[i+1]
                alpha = int(80 * (1 - (current_time - t1) / wave['duration']))
                color = self._normalize_color(base_color, alpha)
                pygame.draw.line(
                    self.screen, 
                    color, 
                    (x1, y1), 
                    (x2, y2), 
                    1
                )
                
    def _draw_game_status(self, game_won, game_over, colors):
        """Отрисовка статуса игры (победа/поражение)"""
        if game_won:
            text = self.font_large.render(
                "ТЫ ПОБЕДИЛ!", 
                True, 
                self._normalize_color(colors['exit'])[:3]
            )
            self._draw_centered_text(text)
        elif game_over:
            text = self.font_large.render(
                "ИГРА ОКОНЧЕНА", 
                True, 
                self._normalize_color(colors['danger'])[:3]
            )
            self._draw_centered_text(text)
            
    def _draw_centered_text(self, text_surface):
        """Отрисовка текста по центру экрана"""
        self.screen.blit(
            text_surface, 
            (
                Config.WIDTH // 2 - text_surface.get_width() // 2, 
                Config.HEIGHT // 2 - text_surface.get_height() // 2
            )
        )
        
    def _draw_ui_buttons(self):
        """Отрисовка кнопок интерфейса"""
        buttons = [
            (10, 10, 100, 30, "Рестарт"),
            (120, 10, 100, 30, "Меню"),
            (230, 10, 100, 30, "Путь")
        ]
        
        for x, y, w, h, text in buttons:
            rect = pygame.Rect(x, y, w, h)
            pygame.draw.rect(self.screen, Config.WHITE, rect)
            
            text_surface = self.font.render(text, True, Config.BLACK)
            self.screen.blit(
                text_surface, 
                (
                    rect.centerx - text_surface.get_width() // 2,
                    rect.centery - text_surface.get_height() // 2
                )
            )