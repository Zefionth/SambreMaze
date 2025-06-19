"""Контроллер игрового процесса"""
import pygame
import math
from src.model.game_model import GameModel
from src.model.particle import Particle
from src.view.game_view import GameView
from src.config import Config

class GameController:
    def __init__(self, screen, sounds):
        self.screen = screen
        self.sounds = sounds
        self.settings = Config.load_settings()
        self.model = GameModel(self.settings)
        self.view = GameView(screen)
        self.return_to_menu = False
        self.show_path = False
        self.game_won_sound_played = False
        self.game_over_sound_played = False

    def start_game(self):
        """Начинает новую игру"""
        self.model = GameModel(self.settings)
        self.return_to_menu = False
        self.game_won_sound_played = False
        self.game_over_sound_played = False

    def handle_events(self) -> bool:
        """Обрабатывает игровые события"""
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ
                    # Проверка кнопок интерфейса
                    if 10 <= mouse_pos[0] <= 110 and 10 <= mouse_pos[1] <= 40:  # Restart
                        self.sounds['click'].play()
                        self.start_game()
                    elif 120 <= mouse_pos[0] <= 220 and 10 <= mouse_pos[1] <= 40:  # Menu
                        self.sounds['click'].play()
                        self.sounds['locator'].stop()
                        self.return_to_menu = True
                    elif 230 <= mouse_pos[0] <= 330 and 10 <= mouse_pos[1] <= 40:  # Show Path
                        self.sounds['click'].play()
                        self.model.show_path = not self.model.show_path
                        if self.model.show_path:
                            self.model.find_path_to_exit()
                        else:
                            self.model.path = []
                    else:
                        self.model.left_mouse_down = True
                        self.sounds['locator'].play()
                elif event.button == 3:  # ПКМ - детектор
                    self.sounds['detector'].play()
                    self.handle_detector_scan(current_time, mouse_pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.model.left_mouse_down = False
                    self.sounds['locator'].stop()

        return True

    def handle_detector_scan(self, current_time, mouse_pos):
        """Обрабатывает активацию детектора"""
        if current_time - self.model.last_detector_time > self.settings['detector_cooldown']:
            self.model.last_detector_time = current_time
            angle = math.atan2(
                mouse_pos[1]-self.model.player.pos[1], 
                mouse_pos[0]-self.model.player.pos[0]
            )
            
            # Создаем волну сканирования
            wave_points, hit_positions = self.model.add_detector_wave(
                self.model.player.pos, angle)
            
            # Границы конуса сканирования
            left_bound, right_bound = [], []
            for dist in range(0, self.settings['fog_radius'], Config.DETECTOR_SCAN_STEP):
                angle_left = angle - math.radians(Config.DETECTOR_ANGLE_MIN)
                angle_right = angle + math.radians(Config.DETECTOR_ANGLE_MIN)
                
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
            self.model.detector_lines.append({
                'points': wave_points,
                'left_bound': left_bound,
                'right_bound': right_bound,
                'start_time': current_time,
                'duration': Config.DETECTOR_WAVE_DURATION,
                'hit_positions': hit_positions,
                'hit_revealed': [False]*len(hit_positions)
            })

            # Добавляем эффекты для обнаруженных опасных зон
            for pos in hit_positions:
                self.model.detector_points.append((*pos, current_time))
                self.model.particles.append(Particle(
                    pos[0], pos[1], 
                    self.settings['colors']['detector'],
                    Config.PARTICLE_SIZE, 
                    Config.PARTICLE_LIFETIME
                ))
                
    def apply_settings(self, settings):
        """Применяет настройки с обновлением слайдеров"""
        self.settings = settings
        
        # Основные настройки
        self.model.player.radius = settings.get('player_radius', 10)
        self.model.player.speed = settings.get('player_speed', 3.5)
        self.model.player.speed_diagonal = self.model.player.speed * 0.7071
        self.model.player.color = settings['colors']['player']
        
        # Параметры игры
        self.fog_radius = settings.get('fog_radius', 150)
        self.point_lifetime = settings.get('point_lifetime', 2500)
        self.locator_cooldown = settings.get('locator_cooldown', 25)
        self.detector_cooldown = settings.get('detector_cooldown', 500)
        self.colors = settings['colors']
        
    def check_ui_buttons(self, mouse_pos):
        """Проверяет нажатия на кнопки интерфейса"""
        if 10 <= mouse_pos[0] <= 110 and 10 <= mouse_pos[1] <= 40:  # Restart
            self.sounds['click'].play()
            self.start_game()
        elif 120 <= mouse_pos[0] <= 220 and 10 <= mouse_pos[1] <= 40:  # Menu
            self.sounds['click'].play()
            self.sounds['locator'].stop()
            self.return_to_menu = True

    def update(self, dt: float):
        """Обновляет игровое состояние"""
        mouse_pos = pygame.mouse.get_pos()
        keys_pressed = pygame.key.get_pressed()
        self.model.update(dt, mouse_pos, keys_pressed)
        
        # Постоянный звук локатора при зажатой ЛКМ
        if self.model.left_mouse_down:
            if not pygame.mixer.get_busy() or pygame.mixer.Sound.get_num_channels(self.sounds['locator']) == 0:
                self.sounds['locator'].play(loops=-1)
        
        # Воспроизведение звуков победы/поражения
        if self.model.game_won and not self.game_won_sound_played:
            self.sounds['win'].play()
            self.game_won_sound_played = True
            self.sounds['locator'].stop()
        
        if self.model.game_over and not self.game_over_sound_played:
            self.sounds['lose'].play()
            self.game_over_sound_played = True
            self.sounds['locator'].stop()

    def draw(self):
        """Отрисовывает игровое состояние"""
        game_state = {
            'player': self.model.player,
            'maze': self.model.maze,
            'thin_walls': self.model.thin_walls,
            'danger_zones': self.model.danger_zones,
            'particles': self.model.particles,
            'locator_points': self.model.locator_points,
            'detector_points': self.model.detector_points,
            'detector_lines': self.model.detector_lines,
            'game_won': self.model.game_won,
            'game_over': self.model.game_over,
            'colors': self.settings['colors'],
            'fog_radius': self.settings['fog_radius'],
            'cell_size': self.model.cell_size,
            'show_path': self.model.show_path,
            'path': self.model.path,
            'point_lifetime': self.settings['point_lifetime']
        }
        self.view.draw(game_state)