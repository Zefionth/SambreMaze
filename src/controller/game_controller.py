"""Контроллер игрового процесса.

Этот модуль содержит класс GameController, который управляет логикой игры,
обработкой событий, обновлением состояния игры и взаимодействием между моделью и представлением.
"""

import pygame
import math
from pygame import mixer
from typing import Dict, Tuple, Any
from src.model.game_model import GameModel
from src.model.particle import Particle
from src.view.game_view import GameView
from src.config import Config


class GameController:
    """Основной контроллер для управления игровым процессом.
    
    Отвечает за:
    - Обработку пользовательского ввода
    - Обновление игрового состояния
    - Управление звуковыми эффектами
    - Взаимодействие между моделью и представлением
    - Применение настроек игры
    
    Attributes:
        screen (pygame.Surface): Игровое окно для отрисовки
        sounds (Dict[str, pygame.mixer.Sound]): Словарь звуковых эффектов
        settings (Dict[str, Any]): Текущие настройки игры
        model (GameModel): Модель игрового состояния
        view (GameView): Представление для отрисовки игры
        return_to_menu (bool): Флаг возврата в меню
        game_won_sound_played (bool): Флаг воспроизведения звука победы
        game_over_sound_played (bool): Флаг воспроизведения звука поражения
        locator_sound_playing (bool): Флаг активности звука локатора
        last_detector_time (int): Время последнего использования детектора
    """
    
    def __init__(self, screen: pygame.Surface, sounds: Dict[str, mixer.Sound]) -> None:
        """Инициализирует контроллер игры.
        
        Args:
            screen: Поверхность Pygame для отрисовки
            sounds: Словарь звуковых эффектов игры
        """
        self.screen = screen
        self.sounds = sounds
        self.settings = Config.load_settings()
        self.model = GameModel(self.settings)
        self.view = GameView(screen)
        self.return_to_menu = False
        self.game_won_sound_played = False
        self.game_over_sound_played = False
        self.locator_sound_playing = False
        self.last_detector_time = 0

    def start_game(self) -> None:
        """Начинает новую игру, сбрасывая все состояния."""
        self.model = GameModel(self.settings)
        self.return_to_menu = False
        self.game_won_sound_played = False
        self.game_over_sound_played = False
        self.locator_sound_playing = False
        self.last_detector_time = 0

    def handle_events(self) -> bool:
        """Обрабатывает игровые события.
        
        Returns:
            bool: False если игра должна завершиться, иначе True
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_button_down(event)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouse_button_up(event)
                
        return True

    def _handle_mouse_button_down(self, event: pygame.event.Event) -> None:
        """Обрабатывает нажатие кнопки мыши.
        
        Args:
            event: Событие мыши Pygame
        """
        mouse_pos = pygame.mouse.get_pos()
        
        if event.button == 1:  # ЛКМ
            if self._is_ui_button_clicked(mouse_pos):
                return
            elif not self.model.game_won and not self.model.game_over:
                self._handle_locator_activation()
                
        elif event.button == 3:  # ПКМ
            if not self.model.game_won and not self.model.game_over:
                self._handle_detector_activation(mouse_pos)

    def _handle_mouse_button_up(self, event: pygame.event.Event) -> None:
        """Обрабатывает отпускание кнопки мыши.
        
        Args:
            event: Событие мыши Pygame
        """
        if event.button == 1:  # ЛКМ
            self.model.left_mouse_down = False
            self._stop_locator_sound()

    def _is_ui_button_clicked(self, mouse_pos: Tuple[int, int]) -> bool:
        """Проверяет клик по UI-кнопкам.
        
        Args:
            mouse_pos: Позиция курсора (x, y)
            
        Returns:
            bool: True если клик был по UI-кнопке, иначе False
        """
        # рестарт
        if 10 <= mouse_pos[0] <= 110 and 10 <= mouse_pos[1] <= 40:
            self.sounds['click'].play()
            self.start_game()
            return True
            
        # меню
        elif 120 <= mouse_pos[0] <= 220 and 10 <= mouse_pos[1] <= 40:
            self.sounds['click'].play()
            self._stop_locator_sound()
            self.return_to_menu = True
            return True
            
        # путь
        elif 230 <= mouse_pos[0] <= 330 and 10 <= mouse_pos[1] <= 40:
            self.sounds['click'].play()
            self.model.show_path = not self.model.show_path
            if self.model.show_path:
                self.model.find_path_to_exit()
            else:
                self.model.path = []
            return True
                
        return False

    def _handle_locator_activation(self) -> None:
        """Активирует локатор и воспроизводит соответствующий звук."""
        self.model.left_mouse_down = True
        if not self.locator_sound_playing:
            self.sounds['locator'].play(loops=-1)
            self.locator_sound_playing = True

    def _handle_detector_activation(self, mouse_pos: Tuple[int, int]) -> None:
        """Активирует детектор с учетом времени перезарядки.
        
        Args:
            mouse_pos: Позиция курсора (x, y)
        """
        current_time = pygame.time.get_ticks()
        detector_cooldown = self.settings['detector_cooldown']
        
        if current_time - self.last_detector_time >= detector_cooldown:
            self.sounds['detector'].play()
            self._perform_detector_scan(current_time, mouse_pos)
            self.last_detector_time = current_time

    def _perform_detector_scan(
        self, 
        current_time: int, 
        mouse_pos: Tuple[int, int]
    ) -> None:
        """Выполняет сканирование детектором и создает визуальные эффекты.
        
        Args:
            current_time: Текущее время в миллисекундах
            mouse_pos: Позиция курсора (x, y)
        """
        angle = math.atan2(
            mouse_pos[1] - self.model.player.pos[1],
            mouse_pos[0] - self.model.player.pos[0]
        )
        
        # данные сканирования из модели
        wave_points, hit_positions = self.model.add_detector_wave(
            self.model.player.pos, 
            angle
        )
        
        # границы конуса сканирования
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

        # данные волны в модели
        self.model.detector_lines.append({
            'points': wave_points,
            'left_bound': left_bound,
            'right_bound': right_bound,
            'start_time': current_time,
            'duration': Config.DETECTOR_WAVE_DURATION,
            'hit_positions': hit_positions,
            'hit_revealed': [False] * len(hit_positions)
        })

        # визуальные эффекты для опасных зон
        for pos in hit_positions:
            self.model.detector_points.append((*pos, current_time))
            self.model.particles.append(Particle(
                pos[0], pos[1],
                self.settings['colors']['detector'],
                Config.PARTICLE_SIZE,
                Config.PARTICLE_LIFETIME
            ))

    def apply_settings(self, settings: Dict[str, Any]) -> None:
        """Применяет новые настройки игры.
        
        Args:
            settings: Словарь с настройками игры
        """
        self.settings = settings
        
        # обновление параметров игрока
        self.model.player.radius = settings.get('player_radius', 10)
        self.model.player.speed = settings.get('player_speed', 3.5)
        self.model.player.speed_diagonal = self.model.player.speed * 0.7071
        self.model.player.color = settings['colors']['player']
        
        # обновление игровых параметров
        self.fog_radius = settings.get('fog_radius', 150)
        self.point_lifetime = settings.get('point_lifetime', 2500)
        self.locator_cooldown = settings.get('locator_cooldown', 25)
        self.detector_cooldown = settings.get('detector_cooldown', 500)
        self.colors = settings['colors']

    def update(self, dt: float) -> None:
        """Обновляет игровое состояние.
        
        Args:
            dt: Время, прошедшее с предыдущего обновления (в секундах)
        """
        mouse_pos = pygame.mouse.get_pos()
        keys_pressed = pygame.key.get_pressed()
        
        if not self.model.game_won and not self.model.game_over:
            self.model.update(dt, mouse_pos, keys_pressed)
        
        self._handle_locator_sound()
        self._play_game_status_sounds()

    def _handle_locator_sound(self) -> None:
        """Управляет воспроизведением звука локатора."""
        if self.model.game_won or self.model.game_over:
            self._stop_locator_sound()
            return
            
        if self.model.left_mouse_down:
            if not mixer.get_busy() or mixer.Sound.get_num_channels(self.sounds['locator']) == 0:
                self.sounds['locator'].play(loops=-1)
        elif self.locator_sound_playing:
            self._stop_locator_sound()

    def _stop_locator_sound(self) -> None:
        """Останавливает звук локатора и сбрасывает флаги."""
        if self.locator_sound_playing:
            self.sounds['locator'].stop()
            self.locator_sound_playing = False
            self.model.left_mouse_down = False

    def _play_game_status_sounds(self) -> None:
        """Воспроизводит звуки победы или поражения при соответствующих условиях."""
        if self.model.game_won and not self.game_won_sound_played:
            self.sounds['win'].play()
            self.game_won_sound_played = True
            self._stop_locator_sound()
        
        if self.model.game_over and not self.game_over_sound_played:
            self.sounds['lose'].play()
            self.game_over_sound_played = True
            self._stop_locator_sound()

    def draw(self) -> None:
        """Отрисовывает текущее состояние игры."""
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