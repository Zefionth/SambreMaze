"""Визуальное представление игрового процесса"""
import pygame
import math
from pygame import gfxdraw
from src.config import Config
from src.utils import normalize_color, center_text, draw_circle

class GameView:
    def __init__(self, screen):
        self.screen = screen
        self._init_fonts()
        self._init_surfaces()
        
    def _init_fonts(self):
        """Инициализация шрифтов"""
        # Используем константы из Config вместо "магических чисел"
        self.font = pygame.font.SysFont(Config.FONT_NAME, Config.UI_FONT_SIZE)
        self.font_large = pygame.font.SysFont(Config.FONT_NAME, Config.SETTINGS_FONT_SIZE)
        
    def _init_surfaces(self):
        """Инициализация поверхностей для эффектов"""
        self.fog_surface = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
        self.pulse_time = 0
        self.fog_surface.fill((0, 0, 0, Config.FOG_ALPHA))
        
    def draw(self, game_state):
        """Основной метод отрисовки игрового состояния"""
        self._clear_screen(Config.DARK)
        self._draw_game_world(game_state)
        self._draw_ui(game_state)
        pygame.display.flip()
        self.pulse_time += Config.PULSE_SPEED
        
    def _clear_screen(self, bg_color):
        """Очистка экрана с заданным цветом"""
        self.screen.fill(normalize_color(bg_color))
        
    def _draw_game_world(self, game_state):
        """Отрисовка игрового мира"""
        if game_state['show_path']:
            self._draw_path(game_state['path'], game_state['cell_size'], game_state['colors']['exit'])
            
        self._create_fog(game_state['player'].pos, game_state['fog_radius'])
        self._draw_particles(game_state['particles'])
        self._draw_player(game_state['player'], game_state['colors']['player'])
        self._draw_exit(game_state['maze'], game_state['cell_size'], game_state['colors']['exit'])
        
        # Отрисовка точек локатора
        self._draw_points(
            game_state['locator_points'], 
            game_state['colors']['locator'], 
            Config.LOCATOR_PULSE_FACTOR, 
            Config.LOCATOR_BASE_RADIUS,
            game_state['point_lifetime']
        )
        
        # Отрисовка точек и волн детектора
        self._draw_points(
            game_state['detector_points'], 
            game_state['colors']['detector'], 
            Config.DETECTOR_PULSE_FACTOR, 
            Config.DETECTOR_BASE_RADIUS,
            game_state['point_lifetime']
        )
        self._draw_detector_waves(game_state['detector_lines'], game_state['colors']['detector'])
        
        if self.fog_surface:
            self.screen.blit(self.fog_surface, (0, 0))
            
    def _draw_ui(self, game_state):
        """Отрисовка интерфейса пользователя"""
        # Убрали неиспользуемый параметр colors
        self._draw_game_status(game_state['game_won'], game_state['game_over'])
        self._draw_ui_buttons()
        
    def _create_fog(self, player_pos, fog_radius):
        """Создание эффекта тумана войны"""
        self.fog_surface.fill((0, 0, 0, Config.FOG_ALPHA))
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
                normalize_color(color), 
                start, 
                end, 
                Config.PATH_LINE_WIDTH
            )
            
    def _draw_points(self, points, base_color, pulse_factor, base_radius, point_lifetime):
        """Отрисовка точек с эффектом пульсации"""
        current_time = pygame.time.get_ticks()
        
        for point in points:
            x, y, t = point
            age = (current_time - t) / point_lifetime
            
            if age >= 1.0:
                continue
                
            alpha = int(255 * (1 - age))
            pulse = math.sin(self.pulse_time) * pulse_factor
            radius = int(base_radius + pulse)
            color = normalize_color(base_color, alpha)
            
            draw_circle(self.screen, x, y, radius, color)
            
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
        
        # Исправлен расчет позиции игрока
        points = [
            (
                player.pos[0] + math.cos(angle) * player.radius * Config.PLAYER_DIRECTION_SIZE,
                player.pos[1] + math.sin(angle) * player.radius * Config.PLAYER_DIRECTION_SIZE
            ),
            (
                player.pos[0] + math.cos(angle + Config.PLAYER_WING_ANGLE) * player.radius * Config.PLAYER_WING_SIZE,
                player.pos[1] + math.sin(angle + Config.PLAYER_WING_ANGLE) * player.radius * Config.PLAYER_WING_SIZE
            ),
            (
                player.pos[0] + math.cos(angle - Config.PLAYER_WING_ANGLE) * player.radius * Config.PLAYER_WING_SIZE,
                player.pos[1] + math.sin(angle - Config.PLAYER_WING_ANGLE) * player.radius * Config.PLAYER_WING_SIZE
            )
        ]
        
        alpha = Config.PLAYER_GLOW_MIN + int(player.glow * Config.PLAYER_GLOW_FACTOR)
        alpha = min(255, max(Config.PLAYER_GLOW_MIN, alpha))
        color = normalize_color(base_color, alpha)
        
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
                        normalize_color(base_color), 
                        exit_rect
                    )
                    
                    pulse = math.sin(self.pulse_time) * Config.EXIT_PULSE_SIZE
                    pygame.draw.rect(
                        self.screen, 
                        normalize_color(base_color, Config.EXIT_GLOW_ALPHA), 
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
            alpha = int(Config.DETECTOR_ALPHA * (1 - (current_time - t) / wave['duration']))
            color = normalize_color(base_color, alpha)
            draw_circle(self.screen, x, y, Config.DETECTOR_POINT_SIZE, color)
            
    def _draw_wave_lines(self, wave, base_color, current_time):
        """Отрисовка линий волны"""
        for bound in [wave['left_bound'], wave['right_bound']]:
            for i in range(len(bound) - 1):
                x1, y1, t1 = bound[i]
                x2, y2, _ = bound[i+1]
                alpha = int(Config.DETECTOR_LINE_ALPHA * (1 - (current_time - t1) / wave['duration']))
                color = normalize_color(base_color, alpha)
                pygame.draw.line(
                    self.screen, 
                    color, 
                    (x1, y1), 
                    (x2, y2), 
                    Config.DETECTOR_LINE_WIDTH
                )
                
    def _draw_game_status(self, game_won, game_over):
        """Отрисовка статуса игры (победа/поражение)"""
        # Убрали неиспользуемый параметр colors
        if game_won:
            text = self.font_large.render(
                "ТЫ ПОБЕДИЛ!", 
                True, 
                Config.GREEN
            )
            self._draw_centered_text(text)
        elif game_over:
            text = self.font_large.render(
                "ИГРА ОКОНЧЕНА", 
                True, 
                Config.RED
            )
            self._draw_centered_text(text)
            
    def _draw_centered_text(self, text_surface):
        """Отрисовка текста по центру экрана"""
        self.screen.blit(text_surface, center_text(self.screen, text_surface))
        
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