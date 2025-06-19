"""Главный запускаемый файл игры.

Этот модуль содержит класс Main, который инициализирует игру,
управляет переключением между меню и игровым процессом,
и запускает главный игровой цикл.
"""

import pygame
from src.controller.game_controller import GameController
from src.controller.menu_controller import MenuController
from src.config import Config
from typing import Dict


class Main:
    """Основной класс игры, управляющий инициализацией и игровым циклом.
    
    Отвечает за:
    - Инициализацию Pygame и игрового окна
    - Загрузку звуковых ресурсов
    - Создание контроллеров игры и меню
    - Управление переключением между игровыми состояниями
    - Запуск и выполнение главного игрового цикла
    
    Attributes:
        screen (pygame.Surface): Основная поверхность для отрисовки
        sounds (Dict[str, pygame.mixer.Sound]): Словарь звуковых эффектов
        game_controller (GameController): Контроллер игрового процесса
        menu_controller (MenuController): Контроллер меню
    """
    
    def __init__(self) -> None:
        """Инициализирует игру, создает окно, загружает ресурсы и контроллеры."""
        # Инициализация Pygame и звуковой системы
        pygame.init()
        pygame.mixer.init()
        
        # Создание игрового окна
        self.screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption("Scanner Sombre: Invisible Walls")
        
        # Загрузка звуковых эффектов
        self.sounds = self._load_sounds()
        
        # Создание контроллеров игры и меню
        self.game_controller = GameController(self.screen, self.sounds)
        self.menu_controller = MenuController(self.screen, self.sounds)
        
        # Связываем модель меню с игровым контроллером
        self.menu_controller.model.game = self.game_controller
        
    def _load_sounds(self) -> Dict[str, pygame.mixer.Sound]:
        """Загружает звуковые эффекты и устанавливает их громкость.
        
        Returns:
            Dict[str, pygame.mixer.Sound]: Словарь звуковых эффектов
        """
        sounds = {
            'click': pygame.mixer.Sound('assets/sounds/click.wav'),
            'locator': pygame.mixer.Sound('assets/sounds/locator.wav'),
            'detector': pygame.mixer.Sound('assets/sounds/detector.wav'),
            'win': pygame.mixer.Sound('assets/sounds/win.wav'),
            'lose': pygame.mixer.Sound('assets/sounds/lose.wav')
        }
        
        # Установка громкости для каждого звука
        for sound_name, sound in sounds.items():
            if sound_name in Config.SOUND_VOLUMES:
                sound.set_volume(Config.SOUND_VOLUMES[sound_name])
        
        return sounds
        
    def run(self) -> None:
        """Запускает и выполняет главный игровой цикл."""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # Рассчитываем время, прошедшее с последнего кадра (в секундах)
            dt = clock.tick(60) / 1000.0
            
            if self.menu_controller.active:
                # Обработка событий и отрисовка меню
                running = self.menu_controller.handle_events()
                self.menu_controller.update(dt)
                self.menu_controller.draw()
                
                # Проверка необходимости запуска игры
                if self.menu_controller.start_game:
                    self._start_game()
            else:
                # Обработка событий и отрисовка игры
                running = self.game_controller.handle_events()
                self.game_controller.update(dt)
                self.game_controller.draw()
                
                # Проверка необходимости возврата в меню
                if self.game_controller.return_to_menu:
                    self._return_to_menu()
        
        # Завершение работы Pygame при выходе из цикла
        pygame.quit()

    def _start_game(self) -> None:
        """Запускает новую игру и переключает состояние."""
        self.game_controller.start_game()
        self.menu_controller.active = False
        self.menu_controller.start_game = False

    def _return_to_menu(self) -> None:
        """Возвращает в главное меню и сбрасывает флаги."""
        self.menu_controller.active = True
        self.game_controller.return_to_menu = False


if __name__ == "__main__":
    """Точка входа в приложение. Создает и запускает игру."""
    game = Main()
    game.run()