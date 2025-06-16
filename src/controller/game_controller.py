"""Контроллер игрового процесса"""
import pygame
import math
from src.model.game_model import GameModel
from src.view.game_view import GameView
from src.model.particle import Particle
from src.config import Config

class GameController:
    def __init__(self, screen):
        self.screen = screen
        self.settings = Config.load_settings()
        self.model = GameModel(self.settings)
        self.view = GameView(screen)
        self.return_to_menu = False

    def start_game(self):
        """Начинает новую игру"""
        self.model = GameModel(self.settings)
        self.return_to_menu = False

    def handle_events(self) -> bool:
        """Обрабатывает игровые события"""
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ - белый скан
                    self.model.left_mouse_down = True
                elif event.button == 3:  # ПКМ - красный скан
                    self.handle_red_scan(current_time, mouse_pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.model.left_mouse_down = False

        # Проверка кнопок интерфейса
        if pygame.mouse.get_pressed()[0]:
            self.check_ui_buttons(pygame.mouse.get_pos())

        return True

    def handle_red_scan(self, current_time, mouse_pos):
        """Обрабатывает активацию красного скана"""
        if current_time - self.model.last_red_scan_time > self.settings['red_scan_cooldown']:
            self.model.last_red_scan_time = current_time
            angle = math.atan2(mouse_pos[1]-self.model.player.pos[1], 
                             mouse_pos[0]-self.model.player.pos[0])
            
            # Создаем волну сканирования
            wave_points, hit_positions = self.model.add_red_scan_wave(
                self.model.player.pos, angle)
            
            # Границы конуса сканирования
            left_bound, right_bound = [], []
            for dist in range(0, self.settings['fog_radius'], 3):
                angle_left = angle - math.radians(45)
                angle_right = angle + math.radians(45)
                
                left_bound.append((
                    self.model.player.pos[0] + math.cos(angle_left) * dist,
                    self.model.player.pos[1] + math.sin(angle_left) * dist,
                    current_time
                ))
                
                right_bound.append((
                    self.model.player.pos[0] + math.cos(angle_right) * dist,
                    self.model.player.pos[1] + math.sin(angle_right) * dist,
                    current_time
                ))

            # Добавляем скан в модель
            self.model.red_scan_lines.append({
                'points': wave_points,
                'left_bound': left_bound,
                'right_bound': right_bound,
                'start_time': current_time,
                'duration': 500,
                'hit_positions': hit_positions,
                'hit_revealed': [False]*len(hit_positions)
            })

            # Добавляем эффекты для обнаруженных опасных зон
            for pos in hit_positions:
                self.model.red_points.append((*pos, current_time))
                self.model.particles.append(Particle(
                    pos[0], pos[1], 
                    self.settings['colors']['danger'], 2, 1.0))

    def check_ui_buttons(self, mouse_pos):
        """Проверяет нажатия на кнопки интерфейса"""
        if 10 <= mouse_pos[0] <= 110 and 10 <= mouse_pos[1] <= 40:  # Restart
            self.start_game()
        elif 120 <= mouse_pos[0] <= 220 and 10 <= mouse_pos[1] <= 40:  # Menu
            self.return_to_menu = True

    def update(self, dt: float):
        """Обновляет игровое состояние"""
        mouse_pos = pygame.mouse.get_pos()
        keys_pressed = pygame.key.get_pressed()
        self.model.update(dt, mouse_pos, keys_pressed)

    def draw(self):
        """Отрисовывает игровое состояние"""
        self.view.draw(
            player=self.model.player,
            maze=self.model.maze,
            thin_walls=self.model.thin_walls,
            red_zones=self.model.red_zones,
            particles=self.model.particles,
            white_points=self.model.white_points,
            red_points=self.model.red_points,
            red_scan_lines=self.model.red_scan_lines,
            game_won=self.model.game_won,
            game_over=self.model.game_over,
            colors=self.settings['colors'],
            fog_radius=self.settings['fog_radius'],
            cell_size=self.model.cell_size
        )