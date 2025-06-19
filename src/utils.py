"""Вспомогательные утилиты"""
import pygame

def center_text(surface, text_surface) -> tuple:
    """Центрирует текст на поверхности"""
    return (
        surface.get_width() // 2 - text_surface.get_width() // 2,
        surface.get_height() // 2 - text_surface.get_height() // 2
    )

def normalize_color(color, alpha=255) -> tuple:
    """Приводит цвет к формату (R, G, B, A)"""
    if isinstance(color, list):
        color = tuple(color)
    return color if len(color) == 4 else (*color[:3], alpha)

def is_valid_cell(cell_x: int, cell_y: int, maze: list) -> bool:
    """Проверяет, находится ли клетка в пределах лабиринта"""
    return (0 <= cell_x < len(maze[0]) and 
            0 <= cell_y < len(maze))

def draw_circle(surface, x, y, radius, color):
    """Универсальный метод отрисовки круга"""
    try:
        pygame.gfxdraw.filled_circle(surface, int(x), int(y), radius, color)
    except:
        pygame.draw.circle(surface, color[:3], (int(x), int(y)), radius)