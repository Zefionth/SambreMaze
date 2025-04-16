import pygame
import math
from maze.generator import MazeGenerator
from entities.player import Player
from rendering.renderer import Renderer
from entities.scanner import Scanner, ScanType
from game.game_state import GameState

class Game:
    def __init__(self, config):
        self.config = config
        self.screen = pygame.display.set_mode((config.width, config.height))
        pygame.display.set_caption(config.title)
        self.clock = pygame.time.Clock()
        self.state = GameState.RUNNING
        
        self.maze_generator = MazeGenerator(config)
        self.maze = self.maze_generator.generate()
        self.player = Player(
            start_pos=config.player_start_pos,
            radius=config.player_radius,
            speed=config.player_speed
        )
        self.scanner = Scanner(config)
        self.renderer = Renderer(self.screen, config)
        
        self.last_red_scan_time = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = GameState.EXIT
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_white_scan(pygame.mouse.get_pos())
                elif event.button == 3:  # Right click
                    self.handle_red_scan(pygame.mouse.get_pos())

    def handle_white_scan(self, mouse_pos):
        current_time = pygame.time.get_ticks()
        new_points = self.scanner.white_scan(self.player.pos, mouse_pos, current_time)
        self.scanner.white_points.extend(new_points)

    def handle_red_scan(self, mouse_pos):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_red_scan_time < self.config.red_scan_cooldown:
            return
            
        self.last_red_scan_time = current_time
        new_points = self.scanner.red_scan(self.player.pos, mouse_pos, current_time)
        self.scanner.red_points.extend(new_points)

    def update(self):
        if self.state != GameState.RUNNING:
            return
            
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] - keys[pygame.K_a]) * self.player.speed
        dy = (keys[pygame.K_s] - keys[pygame.K_w]) * self.player.speed
        
        reached_exit = self.player.move(dx, dy, self.maze)
        if reached_exit:
            self.state = GameState.VICTORY
        elif self.maze.is_red_zone(int(self.player.pos[0]), int(self.player.pos[1])):
            self.state = GameState.GAME_OVER
            
        current_time = pygame.time.get_ticks()
        self.scanner.clean_old_points(current_time)

    def render(self):
        self.renderer.render_all(
            player=self.player,
            maze=self.maze,
            scanner=self.scanner,
            game_state=self.state
        )

    def run(self):
        while self.state != GameState.EXIT:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        pygame.quit()