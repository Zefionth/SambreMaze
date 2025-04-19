"""Главный запускаемый файл игры"""
import pygame
from src.game import ScannerGame

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    game = ScannerGame()
    game.run()