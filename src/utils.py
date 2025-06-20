"""Вспомогательные утилиты.

Этот модуль содержит набор вспомогательных функций, используемых
в различных частях приложения для решения общих задач.
"""

import pygame
from typing import Tuple, List, Union, Any
from pygame import Surface


def center_text(
    surface: Surface, 
    text_surface: Surface
) -> Tuple[int, int]:
    """Вычисляет позицию для центрирования текста на поверхности.
    
    Args:
        surface: Целевая поверхность для размещения текста
        text_surface: Поверхность с текстом
        
    Returns:
        Tuple[int, int]: Координаты (x, y) для центрированного текста
    """
    return (
        surface.get_width() // 2 - text_surface.get_width() // 2,
        surface.get_height() // 2 - text_surface.get_height() // 2
    )


def normalize_color(
    color: Union[Tuple[int, int, int], Tuple[int, int, int, int], List[int]], 
    alpha: int = 255
) -> Tuple[int, int, int, int]:
    """Приводит цвет к формату (R, G, B, A).
    
    Поддерживает преобразование:
    - Из списка в кортеж
    - Из RGB в RGBA
    - Корректную обработку прозрачности
    
    Args:
        color: Исходный цвет в формате RGB/RGBA (кортеж или список)
        alpha: Значение альфа-канала (по умолчанию 255 - непрозрачный)
        
    Returns:
        Tuple[int, int, int, int]: Цвет в формате RGBA
    """
    # список в кортеж
    if isinstance(color, list):
        color = tuple(color)
    
    # добавление альфа-канала если его нет
    if len(color) == 3:
        return (*color[:3], alpha)
    return color


def is_valid_cell(
    cell_x: int, 
    cell_y: int, 
    maze: List[List[Any]]
) -> bool:
    """Проверяет, находится ли клетка в пределах лабиринта.
    
    Args:
        cell_x: X-координата клетки
        cell_y: Y-координата клетки
        maze: Матрица лабиринта (двумерный список)
        
    Returns:
        bool: True если клетка валидна, иначе False
    """
    return (0 <= cell_x < len(maze[0]) and 
            0 <= cell_y < len(maze))


def draw_circle(
    surface: Surface, 
    x: float, 
    y: float, 
    radius: int, 
    color: Union[Tuple[int, int, int], Tuple[int, int, int, int]]
) -> None:
    """Универсальный метод отрисовки круга.
    
    Пытается использовать сглаженную отрисовку, при невозможности
    использует стандартный метод.
    
    Args:
        surface: Поверхность для отрисовки
        x: X-координата центра круга
        y: Y-координата центра круга
        radius: Радиус круга
        color: Цвет круга в формате RGB/RGBA
    """
    try:
        # попытка использовать сглаженную отрисовку
        pygame.gfxdraw.filled_circle(
            surface, 
            int(x), 
            int(y), 
            radius, 
            color
        )
    except Exception:
        # стандартный метод при ошибке
        pygame.draw.circle(
            surface, 
            color[:3],
            (int(x), int(y)), 
            radius
        )