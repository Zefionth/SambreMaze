from enum import Enum

class GameState(Enum):
    RUNNING = 1
    GAME_OVER = 2
    VICTORY = 3
    EXIT = 4