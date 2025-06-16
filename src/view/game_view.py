"""Визуальное представление игрового процесса"""
import pygame
import math
from pygame import gfxdraw
from src.config import Config

class GameView:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont('Arial', 24)
        self.font_large = pygame.font.SysFont('Arial', 48)
        self.fog_surface = None

    def _ensure_color(self, color, alpha=255):
        """Гарантирует корректный формат цвета (R, G, B, A)"""
        if isinstance(color, list):
            color = tuple(color)
        if len(color) == 3:
            return color + (alpha,)
        return color[:4]  # Берем только первые 4 компонента если цвет длиннее

    def draw(self, player, maze, thin_walls, danger_zones, particles, 
        locator_points, detector_points, detector_lines, game_won, 
        game_over, colors, fog_radius, cell_size, timer_start, 
        timer_duration, show_path, path):
        """Отрисовывает текущее игровое состояние"""
        current_time = pygame.time.get_ticks()
        
        # Таймер с контрастным фоном
        elapsed = (current_time - timer_start) // 1000
        remaining = max(0, timer_duration - elapsed)
        timer_text = f"{remaining // 60}:{remaining % 60:02d}"
        
        # Создаем подложку для таймера
        timer_bg = pygame.Surface((80, 30), pygame.SRCALPHA)
        timer_bg.fill((0, 0, 0, 180))  # Полупрозрачный черный фон
        
        # Выбираем контрастный цвет (белый или черный) в зависимости от фона
        bg_color = colors['background']
        if isinstance(bg_color, list):
            bg_color = tuple(bg_color)
        brightness = sum(bg_color[:3])/3
        timer_color = (0, 0, 0) if brightness > 127 else (255, 255, 255)
        
        self.screen.blit(timer_bg, (Config.WIDTH - 90, 5))
        timer_surface = self.font.render(timer_text, True, timer_color)
        self.screen.blit(timer_surface, (Config.WIDTH - 85, 10))

        # Отрисовка пути
        if show_path and path:
            for i in range(len(path) - 1):
                x1 = path[i][0] * cell_size + cell_size // 2
                y1 = path[i][1] * cell_size + cell_size // 2
                x2 = path[i+1][0] * cell_size + cell_size // 2
                y2 = path[i+1][1] * cell_size + cell_size // 2
                pygame.draw.line(self.screen, colors['exit'], (x1, y1), (x2, y2), 3)
        
        # Очистка экрана
        self.screen.fill(self._ensure_color(colors['background']))

        # Создаем туман войны
        self._create_fog(player.pos, fog_radius)

        # Рисуем точки локатора и обновляем список
        locator_points[:] = self._draw_points(locator_points, current_time, 
                                            colors['locator'], 2500, 1.5, 3)

        # Рисуем точки детектора и обновляем список
        detector_points[:] = self._draw_points(detector_points, current_time,
                                            colors['danger'], 2500, 2.0, 1)

        # Рисуем волны детектора
        self._draw_detector_waves(detector_lines, current_time, colors['detector'])

        # Рисуем частицы
        for p in particles:
            p.draw(self.screen)

        # Рисуем игрока
        self._draw_player(player, colors['player'])

        # Рисуем выход
        self._draw_exit(maze, cell_size, current_time, colors['exit'])

        # Наложение тумана
        if self.fog_surface:
            self.screen.blit(self.fog_surface, (0, 0))

        # Сообщения о победе/поражении
        self._draw_game_status(game_won, game_over, colors)

        # Кнопки интерфейса
        self._draw_ui_buttons()

        pygame.display.flip()

    def _create_fog(self, player_pos, fog_radius):
        """Создает поверхность для тумана войны"""
        self.fog_surface = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
        self.fog_surface.fill((0, 0, 0, 200))
        gfxdraw.filled_circle(self.fog_surface, int(player_pos[0]), int(player_pos[1]), 
                            fog_radius, (0, 0, 0, 0))

    def _draw_points(self, points, current_time, base_color, lifetime, pulse_factor, base_radius):
        """Отрисовывает точки с эффектом исчезновения"""
        points_to_keep = []
        
        for point in points:
            x, y, t = point
            age = (current_time - t) / lifetime
            
            # Если точка слишком старая - пропускаем ее
            if age >= 1.0:
                continue
                
            points_to_keep.append(point)
            alpha = int(255 * (1 - age))
            pulse = math.sin(current_time/200) * pulse_factor
            radius = int(base_radius + pulse)
            color = self._ensure_color(base_color, alpha)
            
            try:
                gfxdraw.filled_circle(self.screen, int(x), int(y), radius, color)
            except:
                pygame.draw.circle(self.screen, color[:3], (int(x), int(y)), radius)
        
        # Возвращаем только те точки, которые еще не исчезли
        return points_to_keep


    def _draw_detector_waves(self, waves, current_time, base_color):
        """Отрисовывает волны детектора"""
        for wave in waves:
            if current_time - wave['start_time'] < wave['duration']:
                for point in wave['left_bound'] + wave['right_bound']:
                    x, y, t = point
                    alpha = int(150 * (1 - (current_time - t)/wave['duration']))
                    color = self._ensure_color(base_color, alpha)
                    try:
                        gfxdraw.filled_circle(self.screen, int(x), int(y), 1, color)
                    except:
                        pygame.draw.circle(self.screen, color[:3], (int(x), int(y)), 1)

                for bound in [wave['left_bound'], wave['right_bound']]:
                    for i in range(len(bound) - 1):
                        x1, y1, t1 = bound[i]
                        x2, y2, t2 = bound[i+1]
                        alpha = int(80 * (1 - (current_time - t1)/wave['duration']))
                        color = self._ensure_color(base_color, alpha)
                        pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 1)

    def _draw_player(self, player, base_color):
        """Отрисовывает игрока"""
        mouse_pos = pygame.mouse.get_pos()
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
        color = self._ensure_color(base_color, alpha)
        try:
            gfxdraw.filled_polygon(self.screen, points, color)
        except:
            pygame.draw.polygon(self.screen, color[:3], points)

    def _draw_exit(self, maze, cell_size, current_time, base_color):
        """Отрисовывает выход из лабиринта"""
        for y in range(len(maze)):
            for x in range(len(maze[0])):
                if maze[y][x] == 2:
                    exit_rect = pygame.Rect(x*cell_size, y*cell_size, 
                                          cell_size, cell_size)
                    pygame.draw.rect(self.screen, self._ensure_color(base_color), exit_rect)
                    pulse = math.sin(current_time/500) * 3
                    pygame.draw.rect(self.screen, self._ensure_color(base_color, 50), 
                                   exit_rect.inflate(pulse*2, pulse*2))

    def _draw_game_status(self, game_won, game_over, colors):
        """Отрисовывает сообщения о победе/поражении"""
        if game_won:
            text = self.font_large.render("YOU ESCAPED!", True, self._ensure_color(colors['exit'])[:3])
            self.screen.blit(text, (Config.WIDTH//2-text.get_width()//2, 
                                  Config.HEIGHT//2-text.get_height()//2))
        elif game_over:
            text = self.font_large.render("GAME OVER", True, self._ensure_color(colors['danger'])[:3])
            self.screen.blit(text, (Config.WIDTH//2-text.get_width()//2, 
                                  Config.HEIGHT//2-text.get_height()//2))

    def _draw_ui_buttons(self):
        """Отрисовывает кнопки интерфейса"""
        # Кнопка Restart
        restart_rect = pygame.Rect(10, 10, 100, 30)
        pygame.draw.rect(self.screen, Config.WHITE, restart_rect)
        text = self.font.render("Рестарт", True, Config.BLACK)
        self.screen.blit(text, (restart_rect.centerx-text.get_width()//2, 
                          restart_rect.centery-text.get_height()//2))

        # Кнопка Menu
        menu_rect = pygame.Rect(120, 10, 100, 30)
        pygame.draw.rect(self.screen, Config.WHITE, menu_rect)
        text = self.font.render("Меню", True, Config.BLACK)
        self.screen.blit(text, (menu_rect.centerx-text.get_width()//2, 
                          menu_rect.centery-text.get_height()//2))