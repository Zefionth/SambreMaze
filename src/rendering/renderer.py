import pygame
import math
from pygame import gfxdraw
from game.game_state import GameState 

class Renderer:
    def __init__(self, screen, config):
        self.screen = screen
        self.config = config
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 72)
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 50, 50)
        self.GREEN = (0, 255, 0)
        self.BLUE = (100, 100, 255)

    def render_all(self, player, maze, scanner, game_state):
        self.screen.fill(self.BLACK)
        self._render_scan_points(scanner.white_points)
        self._render_red_points(scanner.red_points)
        self._render_maze(maze)
        self._render_player(player)
        self._render_ui(game_state)
        pygame.display.flip()

    def _render_scan_points(self, points):
        current_time = pygame.time.get_ticks()
        for x, y, t in points:
            age = current_time - t
            alpha = 255 - int(255 * (age / 10000))
            if alpha > 0:
                color = (255, 255, 255, alpha)
                pygame.gfxdraw.filled_circle(self.screen, int(x), int(y), 2, color)

    def _render_red_points(self, points):
        current_time = pygame.time.get_ticks()
        for x, y, t in points:
            age = current_time - t
            alpha = 200 - int(200 * (age / 10000))
            if alpha > 0:
                color = (255, 100, 100, alpha)
                pygame.gfxdraw.filled_circle(self.screen, int(x), int(y), 3, color)

    def _render_maze(self, maze):
        for y in range(len(maze.full_maze)):
            for x in range(len(maze.full_maze[0])):
                if maze.full_maze[y][x] == 2:  # Exit
                    exit_rect = pygame.Rect(
                        x * maze.cell_size,
                        y * maze.cell_size,
                        maze.cell_size,
                        maze.cell_size
                    )
                    pygame.draw.rect(self.screen, self.GREEN, exit_rect)

    def _render_player(self, player):
        pygame.draw.circle(
            self.screen, 
            self.WHITE, 
            (int(player.pos[0]), int(player.pos[1])), 
            player.radius
        )
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = player.get_direction_to((mouse_x, mouse_y))
        
        tip_x = player.pos[0] + math.cos(angle) * player.radius * 1.5
        tip_y = player.pos[1] + math.sin(angle) * player.radius * 1.5
        
        left_x = player.pos[0] + math.cos(angle + math.pi * 0.75) * player.radius
        left_y = player.pos[1] + math.sin(angle + math.pi * 0.75) * player.radius
        
        right_x = player.pos[0] + math.cos(angle - math.pi * 0.75) * player.radius
        right_y = player.pos[1] + math.sin(angle - math.pi * 0.75) * player.radius
        
        pygame.draw.polygon(
            self.screen,
            self.BLUE,
            [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)]
        )

    def _render_ui(self, game_state):
        # Render restart button
        restart_rect = pygame.Rect(10, 10, 100, 30)
        pygame.draw.rect(self.screen, self.WHITE, restart_rect)
        restart_text = self.font.render("Restart", True, self.BLACK)
        self.screen.blit(restart_text, (restart_rect.centerx - restart_text.get_width() // 2, 
                                      restart_rect.centery - restart_text.get_height() // 2))

        # Render game messages
        if game_state == GameState.VICTORY:
            win_text = self.big_font.render("You Won!", True, self.GREEN)
            self.screen.blit(win_text, (self.config.width // 2 - win_text.get_width() // 2, 
                                      self.config.height // 2 - win_text.get_height() // 2))
        elif game_state == GameState.GAME_OVER:
            over_text = self.big_font.render("Game Over", True, self.RED)
            self.screen.blit(over_text, (self.config.width // 2 - over_text.get_width() // 2, 
                                       self.config.height // 2 - over_text.get_height() // 2))

        # Render red scanner cooldown
        cooldown_rect = pygame.Rect(self.config.width - 120, 10, 100, 20)
        pygame.draw.rect(self.screen, (50, 50, 50), cooldown_rect)
        cooldown_text = self.font.render("Red Scanner", True, self.WHITE)
        self.screen.blit(cooldown_text, (self.config.width - 120, 32))