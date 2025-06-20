"""Модуль для поиска пути с использованием алгоритма A*.

Этот модуль содержит класс PathFinder, который реализует алгоритм A*
для поиска кратчайшего пути от начальной точки до выхода в лабиринте.
"""

import heapq
from typing import List, Tuple, Dict, Optional


class PathFinder:
    """Класс, реализующий алгоритм A* для поиска пути в лабиринте."""
    
    @staticmethod
    def find_path(
        start: Tuple[int, int], 
        exit_pos: Tuple[int, int], 
        maze: List[List[int]]
    ) -> List[Tuple[int, int]]:
        """Находит кратчайший путь от начальной точки до выхода в лабиринте.
        
        Использует алгоритм A* с манхэттенским расстоянием в качестве эвристики.
        
        Args:
            start: Координаты начальной точки (x, y)
            exit_pos: Координаты точки выхода (x, y)
            maze: Матрица лабиринта (0 - проход, 1 - стена)
            
        Returns:
            List[Tuple[int, int]]: Список точек пути от старта до выхода,
                                    или пустой список если путь не найден.
        """
        # очередь с приоритетом
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        # словари для хранения информации о пути и стоимости
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {}
        g_score: Dict[Tuple[int, int], float] = {start: 0}
        f_score: Dict[Tuple[int, int], float] = {start: PathFinder.heuristic(start, exit_pos)}
        
        while open_set:
            # узел с наименьшей f_score
            current = heapq.heappop(open_set)[1]
            
            if current == exit_pos:
                return PathFinder.reconstruct_path(came_from, current)
                
            # проверка всех соседей текущей клетки
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                
                # пропуск невалидных клеток и стен
                if not PathFinder.is_valid_cell(neighbor[0], neighbor[1], maze):
                    continue
                if maze[neighbor[1]][neighbor[0]] == 1:
                    continue
                    
                # расчет временной g_score
                tentative_g_score = g_score[current] + 1
                
                # если нашли лучший путь к соседу, обновляем данные
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + PathFinder.heuristic(neighbor, exit_pos)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
                    
        return []  # путь не найден

    @staticmethod
    def is_valid_cell(cell_x: int, cell_y: int, maze: List[List[int]]) -> bool:
        """Проверяет, находится ли клетка в пределах лабиринта.
        
        Args:
            cell_x: X-координата клетки
            cell_y: Y-координата клетки
            maze: Матрица лабиринта
            
        Returns:
            bool: True если клетка валидна, иначе False
        """
        return (0 <= cell_x < len(maze[0])) and (0 <= cell_y < len(maze))
    
    @staticmethod
    def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Рассчитывает манхэттенское расстояние между двумя точками.
        
        Args:
            a: Первая точка (x1, y1)
            b: Вторая точка (x2, y2)
            
        Returns:
            int: Манхэттенское расстояние |x1-x2| + |y1-y2|
        """
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    @staticmethod
    def reconstruct_path(
        came_from: Dict[Tuple[int, int], Tuple[int, int]], 
        current: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """Восстанавливает путь от текущей точки до старта.
        
        Args:
            came_from: Словарь связей "узел -> предыдущий узел"
            current: Конечная точка пути
            
        Returns:
            List[Tuple[int, int]]: Путь от старта до конечной точки
        """
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path