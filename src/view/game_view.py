"""Визуальное представление игрового процесса.

Этот модуль содержит класс GameView, который отвечает за отрисовку
всех игровых элементов, интерфейса и визуальных эффектов.
"""

import pygame
import math
from pygame import gfxdraw
from src.config import Config
from src.utils import normalize_color, center_text, draw_circle
from typing import Dict, List, Tuple, Any


class GameView:
    """Класс для визуального представления игрового состояния.
    
    Отвечает за:
    - Отрисовку игрового мира (лабиринт, игрок, выход)
    - Визуализацию эффектов (частицы, сканирование, туман)
    - Отображение интерфейса пользователя
    - Рендеринг состояния игры (победа/поражение)
    
    Attributes:
        screen (pygame.Surface): Основная поверхность для отрисовки
        font (pygame.font.Font): Основной шрифт для UI
        font_large (pygame.font.Font): Крупный шрифт для заголовков
        fog_surface (pygame.Surface): Поверхность для эффекта тумана
        pulse_time (float): Время для пульсации эффектов
    """
    
    def __init__(self, screen: pygame.Surface) -> None:
        """Инициализирует представление игры.
        
        Args:
            screen: Основная поверхность Pygame для отрисовки
        """
        self.screen = screen
        self._init_fonts()
        self._init_surfaces()
        
    def _init_fonts(self) -> None:
        """Инициализирует шрифты для интерфейса."""
        self.font = pygame.font.SysFont(Config.FONT_NAME, Config.UI_FONT_SIZE)
        self.font_large = pygame.font.SysFont(
            Config.FONT_NAME, 
            Config.SETTINGS_FONT_SIZE
        )
        
    def _init_surfaces(self) -> None:
        """Инициализирует поверхности для специальных эффектов."""
        # Создаем поверхность для тумана с альфа-каналом
        self.fog_surface = pygame.Surface(
            (Config.WIDTH, Config.HEIGHT), 
            pygame.SRCALPHA
        )
        self.pulse_time = 0.0
        self.fog_surface.fill((0, 0, 0, Config.FOG_ALPHA))
        
    def draw(self, game_state: Dict[str, Any]) -> None:
        """Основной метод отрисовки игрового состояния.
        
        Args:
            game_state: Словарь с текущим состоянием игры
        """
        self._clear_screen(Config.DARK)
        self._draw_game_world(game_state)
        self._draw_ui(game_state)
        pygame.display.flip()
        self.pulse_time += Config.PULSE_SPEED
        
    def _clear_screen(self, bg_color: Tuple[int, int, int]) -> None:
        """Очищает экран заданным цветом.
        
        Args:
            bg_color: Цвет фона (RGB)
        """
        self.screen.fill(normalize_color(bg_color))
        
    def _draw_game_world(self, game_state: Dict[str, Any]) -> None:
        """Отрисовывает все элементы игрового мира.
        
        Args:
            game_state: Словарь с текущим состоянием игры
        """
        # Отрисовка пути к выходу (если включено)
        if game_state['show_path']:
            self._draw_path(
                game_state['path'], 
                game_state['cell_size'], 
                game_state['colors']['exit']
            )
            
        # Отрисовка эффектов и объектов
        self._create_fog(game_state['player'].pos, game_state['fog_radius'])
        self._draw_particles(game_state['particles'])
        self._draw_player(game_state['player'], game_state['colors']['player'])
        self._draw_exit(
            game_state['maze'], 
            game_state['cell_size'], 
            game_state['colors']['exit']
        )
        
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
        self._draw_detector_waves(
            game_state['detector_lines'], 
            game_state['colors']['detector']
        )
        
        # Наложение тумана
        if self.fog_surface:
            self.screen.blit(self.fog_surface, (0, 0))
            
    def _draw_ui(self, game_state: Dict[str, Any]) -> None:
        """Отрисовывает элементы пользовательского интерфейса.
        
        Args:
            game_state: Словарь с текущим состоянием игры
        """
        self._draw_game_status(game_state['game_won'], game_state['game_over'])
        self._draw_ui_buttons()
        
    def _create_fog(
        self, 
        player_pos: Tuple[float, float], 
        fog_radius: int
    ) -> None:
        """Создает эффект тумана войны вокруг игрока.
        
        Args:
            player_pos: Позиция игрока (x, y)
            fog_radius: Радиус видимости вокруг игрока
        """
        self.fog_surface.fill((0, 0, 0, Config.FOG_ALPHA))
        gfxdraw.filled_circle(
            self.fog_surface, 
            int(player_pos[0]), 
            int(player_pos[1]), 
            fog_radius, 
            (0, 0, 0, 0)  # Прозрачный цвет для "дырки"
        )
        
    def _draw_path(
        self, 
        path: List[Tuple[int, int]], 
        cell_size: int, 
        color: Tuple[int, int, int]
    ) -> None:
        """Отрисовывает путь к выходу.
        
        Args:
            path: Список точек пути
            cell_size: Размер ячейки лабиринта
            color: Цвет пути (RGB)
        """
        if not path:
            return
            
        for i in range(len(path) - 1):
            # Рассчитываем координаты начала и конца сегмента пути
            start = (
                path[i][0] * cell_size + cell_size // 2,
                path[i][1] * cell_size + cell_size // 2
            )
            end = (
                path[i+1][0] * cell_size + cell_size // 2,
                path[i+1][1] * cell_size + cell_size // 2
            )
            
            # Рисуем линию между точками
            pygame.draw.line(
                self.screen, 
                normalize_color(color), 
                start, 
                end, 
                Config.PATH_LINE_WIDTH
            )
            
    def _draw_points(
        self, 
        points: List[Tuple[float, float, int]], 
        base_color: Tuple[int, int, int], 
        pulse_factor: float, 
        base_radius: int,
        point_lifetime: int
    ) -> None:
        """Отрисовывает точки с эффектом пульсации.
        
        Args:
            points: Список точек (x, y, время создания)
            base_color: Базовый цвет точек (RGB)
            pulse_factor: Фактор пульсации
            base_radius: Базовый радиус точек
            point_lifetime: Время жизни точек в миллисекундах
        """
        current_time = pygame.time.get_ticks()
        
        for point in points:
            x, y, t = point
            age = (current_time - t) / point_lifetime
            
            # Пропускаем устаревшие точки
            if age >= 1.0:
                continue
                
            # Рассчитываем прозрачность и радиус с пульсацией
            alpha = int(255 * (1 - age))
            pulse = math.sin(self.pulse_time) * pulse_factor
            radius = int(base_radius + pulse)
            color = normalize_color(base_color, alpha)
            
            # Отрисовываем точку
            draw_circle(self.screen, x, y, radius, color)
            
    def _draw_particles(self, particles: List[Any]) -> None:
        """Отрисовывает все частицы.
        
        Args:
            particles: Список объектов частиц
        """
        for p in particles:
            p.draw(self.screen)
            
    def _draw_player(
        self, 
        player: Any, 
        base_color: Tuple[int, int, int]
    ) -> None:
        """Отрисовывает игрока в виде треугольника.
        
        Args:
            player: Объект игрока
            base_color: Базовый цвет игрока (RGB)
        """
        mouse_pos = pygame.mouse.get_pos()
        angle = math.atan2(
            mouse_pos[1] - player.pos[1], 
            mouse_pos[0] - player.pos[0]
        )
        
        # Рассчитываем вершины треугольника
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
        
        # Рассчитываем прозрачность с учетом свечения
        alpha = Config.PLAYER_GLOW_MIN + int(player.glow * Config.PLAYER_GLOW_FACTOR)
        alpha = min(255, max(Config.PLAYER_GLOW_MIN, alpha))
        color = normalize_color(base_color, alpha)
        
        # Пытаемся использовать сглаженный полигон, иначе обычный
        try:
            gfxdraw.filled_polygon(self.screen, points, color)
        except Exception:
            pygame.draw.polygon(self.screen, color[:3], points)
            
    def _draw_exit(
        self, 
        maze: List[List[int]], 
        cell_size: int, 
        base_color: Tuple[int, int, int]
    ) -> None:
        """Отрисовывает выход из лабиринта.
        
        Args:
            maze: Матрица лабиринта
            cell_size: Размер ячейки лабиринта
            base_color: Базовый цвета выхода (RGB)
        """
        for y in range(len(maze)):
            for x in range(len(maze[0])):
                if maze[y][x] == 2:  # 2 - идентификатор выхода
                    exit_rect = pygame.Rect(
                        x * cell_size, 
                        y * cell_size, 
                        cell_size, 
                        cell_size
                    )
                    
                    # Отрисовываем основной прямоугольник выхода
                    pygame.draw.rect(
                        self.screen, 
                        normalize_color(base_color), 
                        exit_rect
                    )
                    
                    # Создаем пульсирующий эффект свечения
                    pulse = math.sin(self.pulse_time) * Config.EXIT_PULSE_SIZE
                    pygame.draw.rect(
                        self.screen, 
                        normalize_color(base_color, Config.EXIT_GLOW_ALPHA), 
                        exit_rect.inflate(pulse * 2, pulse * 2)
                    )
                    
    def _draw_detector_waves(
        self, 
        waves: List[Dict[str, Any]], 
        base_color: Tuple[int, int, int]
    ) -> None:
        """Отрисовывает волны детектора.
        
        Args:
            waves: Список волн детектора
            base_color: Базовый цвет детектора (RGB)
        """
        current_time = pygame.time.get_ticks()
        
        for wave in waves:
            # Проверяем, активна ли еще волна
            if current_time - wave['start_time'] < wave['duration']:
                self._draw_wave_points(wave, base_color, current_time)
                self._draw_wave_lines(wave, base_color, current_time)
                
    def _draw_wave_points(
        self, 
        wave: Dict[str, Any], 
        base_color: Tuple[int, int, int], 
        current_time: int
    ) -> None:
        """Отрисовывает точки волны детектора.
        
        Args:
            wave: Данные волны детектора
            base_color: Базовый цвет (RGB)
            current_time: Текущее время в миллисекундах
        """
        for point in wave['left_bound'] + wave['right_bound']:
            x, y, t = point
            # Рассчитываем прозрачность на основе оставшегося времени
            alpha = int(Config.DETECTOR_ALPHA * 
                       (1 - (current_time - t) / wave['duration']))
            color = normalize_color(base_color, alpha)
            draw_circle(self.screen, x, y, Config.DETECTOR_POINT_SIZE, color)
            
    def _draw_wave_lines(
        self, 
        wave: Dict[str, Any], 
        base_color: Tuple[int, int, int], 
        current_time: int
    ) -> None:
        """Отрисовывает линии волны детектора.
        
        Args:
            wave: Данные волны детектора
            base_color: Базовый цвет (RGB)
            current_time: Текущее время в миллисекундах
        """
        for bound in [wave['left_bound'], wave['right_bound']]:
            for i in range(len(bound) - 1):
                x1, y1, t1 = bound[i]
                x2, y2, _ = bound[i+1]
                
                # Рассчитываем прозрачность линии
                alpha = int(Config.DETECTOR_LINE_ALPHA * 
                           (1 - (current_time - t1) / wave['duration']))
                color = normalize_color(base_color, alpha)
                
                # Рисуем линию между точками
                pygame.draw.line(
                    self.screen, 
                    color, 
                    (x1, y1), 
                    (x2, y2), 
                    Config.DETECTOR_LINE_WIDTH
                )
                
    def _draw_game_status(self, game_won: bool, game_over: bool) -> None:
        """Отрисовывает статус игры (победа/поражение).
        
        Args:
            game_won: Флаг победы в игре
            game_over: Флаг поражения в игре
        """
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
            
    def _draw_centered_text(self, text_surface: pygame.Surface) -> None:
        """Отрисовывает текст по центру экрана.
        
        Args:
            text_surface: Поверхность с текстом
        """
        self.screen.blit(text_surface, center_text(self.screen, text_surface))
        
    def _draw_ui_buttons(self) -> None:
        """Отрисовывает кнопки пользовательского интерфейса."""
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