"""Главный запускаемый файл игры"""
import pygame
from src.controller.game_controller import GameController
from src.controller.menu_controller import MenuController
from src.config import Config

class Main:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption("Scanner Sombre: Invisible Walls")
        
        self.game_controller = GameController(self.screen)
        self.menu_controller = MenuController(self.screen)
        self.menu_controller.model.game = self.game_controller
        
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            dt = clock.tick(60) / 1000.0
            
            if self.menu_controller.active:
                running = self.menu_controller.handle_events()
                self.menu_controller.update(dt)
                self.menu_controller.draw()
                
                if self.menu_controller.start_game:
                    self.game_controller.start_game()
                    self.menu_controller.active = False
                    self.menu_controller.start_game = False
            else:
                running = self.game_controller.handle_events()
                self.game_controller.update(dt)
                self.game_controller.draw()
                
                if self.game_controller.return_to_menu:
                    self.menu_controller.active = True
                    self.game_controller.return_to_menu = False
        
        pygame.quit()

if __name__ == "__main__":
    game = Main()
    game.run()