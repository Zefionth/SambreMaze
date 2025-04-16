import pygame
import random
import math
from pygame import gfxdraw

# Инициализация Pygame
pygame.init()

# Настройки окна
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Scanner Sombre: Red Zones")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50, 200)  # Более яркий красный
GREEN = (0, 255, 0)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 0)

# Настройки игрока
player_pos = [WIDTH // 2, HEIGHT // 2]
player_radius = 8
player_speed = 4
player_direction = 0

# Точки сканирования
white_points = []  # Белые точки (ЛКМ)
red_points = []    # Красные точки (ПКМ)
point_lifetime = 2500  # 2.5 секунд
red_scan_lines = []  # Для анимации красного сканирования

def generate_maze(width, height, cell_size=30):
    cols = width // cell_size
    rows = height // cell_size
    
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    thin_walls = [[0 for _ in range(cols)] for _ in range(rows)]
    red_zones = []
    
    # Гарантируем свободное пространство 3x3 вокруг центра
    center_x, center_y = cols // 2, rows // 2
    for y in range(center_y - 1, center_y + 2):
        for x in range(center_x - 1, center_x + 2):
            if 0 <= x < cols and 0 <= y < rows:
                maze[y][x] = 0
    
    # Генерация лабиринта
    stack = [(center_x, center_y)]
    
    while stack:
        x, y = stack[-1]
        neighbors = []
        
        if x > 1 and maze[y][x-2] == 1:
            neighbors.append((x-2, y))
        if x < cols - 2 and maze[y][x+2] == 1:
            neighbors.append((x+2, y))
        if y > 1 and maze[y-2][x] == 1:
            neighbors.append((x, y-2))
        if y < rows - 2 and maze[y+2][x] == 1:
            neighbors.append((x, y+2))
        
        if neighbors:
            nx, ny = random.choice(neighbors)
            maze[ny][nx] = 0
            maze[(ny + y) // 2][(nx + x) // 2] = 0
            stack.append((nx, ny))
        else:
            stack.pop()
    
    # Создаем выход
    exit_side = random.randint(0, 3)
    if exit_side == 0:  # верх
        exit_x = random.randint(1, cols-2)
        exit_y = 0
    elif exit_side == 1:  # право
        exit_x = cols - 1
        exit_y = random.randint(1, rows-2)
    elif exit_side == 2:  # низ
        exit_x = random.randint(1, cols-2)
        exit_y = rows - 1
    else:  # лево
        exit_x = 0
        exit_y = random.randint(1, rows-2)
    
    maze[exit_y][exit_x] = 2  # Выход
    
    # Собираем все стены, которые можно заменить на красные зоны
    potential_red_zones = []
    for y in range(rows):
        for x in range(cols):
            if maze[y][x] == 1:
                # Проверяем, что это граница прохода (тонкая стена)
                if (x > 0 and maze[y][x-1] == 0) or (x < cols-1 and maze[y][x+1] == 0) or \
                   (y > 0 and maze[y-1][x] == 0) or (y < rows-1 and maze[y+1][x] == 0):
                    # Не заменяем стены рядом с выходом
                    if abs(x - exit_x) > 2 or abs(y - exit_y) > 2:
                        potential_red_zones.append((x, y))
    
    # Заменяем 30% подходящих стен на красные зоны
    red_zone_count = int(len(potential_red_zones) * 0.3)
    red_zones = random.sample(potential_red_zones, red_zone_count)
    
    # Создаем карту тонких стен (учитывая красные зоны)
    for y in range(rows):
        for x in range(cols):
            if maze[y][x] == 1:
                if (x, y) in red_zones:
                    thin_walls[y][x] = 0  # Красные зоны не отображаются как стены
                elif (x > 0 and maze[y][x-1] == 0) or (x < cols-1 and maze[y][x+1] == 0) or \
                     (y > 0 and maze[y-1][x] == 0) or (y < rows-1 and maze[y+1][x] == 0):
                    thin_walls[y][x] = 1  # Обычные тонкие стены
    
    return thin_walls, maze, red_zones, cell_size, 2

thin_walls, maze, red_zones, cell_size, wall_thickness = generate_maze(WIDTH, HEIGHT)

# Игровой цикл
running = True
game_won = False
game_over = False
clock = pygame.time.Clock()
last_red_scan_time = 0
red_scan_cooldown = 500  # 0.5 секунды между сканами

def reset_game():
    global player_pos, white_points, red_points, game_won, game_over, thin_walls, maze, red_zones, cell_size, wall_thickness, red_scan_lines
    player_pos = [WIDTH // 2, HEIGHT // 2]
    white_points = []
    red_points = []
    red_scan_lines = []
    game_won = False
    game_over = False
    thin_walls, maze, red_zones, cell_size, wall_thickness = generate_maze(WIDTH, HEIGHT)

def add_red_scan_wave(start_pos, angle):
    """Создает волну сканирования на 90 градусов (45 влево и вправо)"""
    length = 200
    wave_points = []
    hit_positions = []
    
    # Сканируем в диапазоне углов
    for delta in range(-45, 46, 5):  # Шаг 5 градусов
        current_angle = angle + math.radians(delta)
        end_pos = (
            start_pos[0] + math.cos(current_angle) * length,
            start_pos[1] + math.sin(current_angle) * length
        )
        
        # Проверяем пересечение с красными зонами
        hit_red_zone = False
        steps = int(length)
        for i in range(1, steps):
            check_x = int(start_pos[0] + math.cos(current_angle) * i)
            check_y = int(start_pos[1] + math.sin(current_angle) * i)
            
            cell_x = check_x // cell_size
            cell_y = check_y // cell_size
            
            if 0 <= cell_x < len(maze[0]) and 0 <= cell_y < len(maze):
                if (cell_x, cell_y) in red_zones:
                    hit_red_zone = True
                    end_pos = (check_x, check_y)
                    hit_positions.append(end_pos)
                    break
        
        # Создаем точки вдоль луча
        steps = int(length)
        for i in range(0, steps, 5):  # Каждые 5 пикселей
            point_pos = (
                start_pos[0] + math.cos(current_angle) * i,
                start_pos[1] + math.sin(current_angle) * i
            )
            
            if hit_red_zone and math.dist(point_pos, start_pos) >= math.dist(end_pos, start_pos):
                break
                
            wave_points.append((*point_pos, pygame.time.get_ticks()))
    
    return wave_points, len(hit_positions) > 0, hit_positions

while running:
    current_time = pygame.time.get_ticks()
    
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3 and current_time - last_red_scan_time > red_scan_cooldown:  # ПКМ с кулдауном
                last_red_scan_time = current_time
                mouse_x, mouse_y = pygame.mouse.get_pos()
                angle = math.atan2(mouse_y - player_pos[1], mouse_x - player_pos[0])
                
                # Создаем волну сканирования
                wave_points, hit_red_zone, hit_positions = add_red_scan_wave(player_pos, angle)
                red_scan_lines.append({
                    'points': wave_points,
                    'start_time': current_time,
                    'duration': 300,
                    'hit_red_zone': hit_red_zone,
                    'hit_positions': hit_positions
                })
                
                # Добавляем постоянные точки для найденных красных зон
                for pos in hit_positions:
                    red_points.append((*pos, current_time))
    
    # Обновляем анимации красного сканирования
    active_scan_lines = []
    for scan_line in red_scan_lines:
        progress = (current_time - scan_line['start_time']) / scan_line['duration']
        
        if progress < 1.0:
            active_scan_lines.append(scan_line)
    red_scan_lines = active_scan_lines
    
    # Движение игрока
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_a]:
        dx -= player_speed
    if keys[pygame.K_d]:
        dx += player_speed
    if keys[pygame.K_w]:
        dy -= player_speed
    if keys[pygame.K_s]:
        dy += player_speed
    
    # Проверка границ окна
    new_x = player_pos[0] + dx
    new_y = player_pos[1] + dy
    
    if new_x - player_radius < 0:
        new_x = player_radius
    if new_x + player_radius > WIDTH:
        new_x = WIDTH - player_radius
    if new_y - player_radius < 0:
        new_y = player_radius
    if new_y + player_radius > HEIGHT:
        new_y = HEIGHT - player_radius
    
    # Проверка столкновений
    can_move = True
    
    # Проверяем красные зоны
    cell_x = int(new_x) // cell_size
    cell_y = int(new_y) // cell_size
    if 0 <= cell_x < len(maze[0]) and 0 <= cell_y < len(maze):
        if (cell_x, cell_y) in red_zones:
            game_over = True
    
    # Проверяем стены
    corners = [
        (new_x - player_radius, new_y - player_radius),
        (new_x + player_radius, new_y - player_radius),
        (new_x - player_radius, new_y + player_radius),
        (new_x + player_radius, new_y + player_radius)
    ]
    
    for corner_x, corner_y in corners:
        cell_x = int(corner_x) // cell_size
        cell_y = int(corner_y) // cell_size
        
        if 0 <= cell_x < len(maze[0]) and 0 <= cell_y < len(maze):
            if thin_walls[cell_y][cell_x] == 1:  # Стена
                can_move = False
                break
            elif maze[cell_y][cell_x] == 2:  # Выход
                game_won = True
    
    if can_move and not game_over:
        player_pos[0] = new_x
        player_pos[1] = new_y
    
    # Сканирование белым лучом (ЛКМ зажата)
    if pygame.mouse.get_pressed()[0]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = math.atan2(mouse_y - player_pos[1], mouse_x - player_pos[0])
        
        for _ in range(3):  # Меньше точек для белого луча
            dist = random.uniform(0, 200)
            end_x = player_pos[0] + math.cos(angle) * dist
            end_y = player_pos[1] + math.sin(angle) * dist
            
            # Проверка столкновения со стенами
            hit_wall = False
            steps = int(dist)
            for i in range(1, steps):
                check_x = int(player_pos[0] + math.cos(angle) * i)
                check_y = int(player_pos[1] + math.sin(angle) * i)
                
                cell_x = check_x // cell_size
                cell_y = check_y // cell_size
                
                if 0 <= cell_x < len(maze[0]) and 0 <= cell_y < len(maze):
                    if thin_walls[cell_y][cell_x] == 1:  # Стена
                        hit_wall = True
                        end_x = player_pos[0] + math.cos(angle) * (i-1)
                        end_y = player_pos[1] + math.sin(angle) * (i-1)
                        break
                    elif maze[cell_y][cell_x] == 2:  # Выход
                        hit_wall = True
                        end_x = check_x
                        end_y = check_y
                        break
            
            white_points.append((end_x, end_y, current_time))
    
    # Удаляем старые точки
    white_points = [(x, y, t) for x, y, t in white_points if current_time - t < point_lifetime]
    red_points = [(x, y, t) for x, y, t in red_points if current_time - t < point_lifetime]
    
    # Отрисовка
    screen.fill(BLACK)
    
    # Рисуем белые точки (стены)
    for x, y, t in white_points:
        age = current_time - t
        alpha = 255 - int(255 * (age / point_lifetime))
        if alpha > 0:
            color = (255, 255, 255, alpha)
            pygame.gfxdraw.filled_circle(screen, int(x), int(y), 2, color)
    
    # Рисуем красные точки (опасные зоны)
    for x, y, t in red_points:
        age = current_time - t
        alpha = 200 - int(200 * (age / point_lifetime))
        if alpha > 0:
            color = (255, 100, 100, alpha)
            pygame.gfxdraw.filled_circle(screen, int(x), int(y), 3, color)
    
    # Рисуем анимированные линии красного сканирования
    for scan_line in red_scan_lines:
        progress = (current_time - scan_line['start_time']) / scan_line['duration']
        visible_points = int(len(scan_line['points']) * progress)
        
        for i in range(visible_points):
            if i < len(scan_line['points']):
                x, y, t = scan_line['points'][i]
                alpha = 255 * (1 - (i / len(scan_line['points'])))
                color = (255, 50, 50, int(alpha))
                pygame.gfxdraw.filled_circle(screen, int(x), int(y), 2, color)
    
    # Рисуем выход, если он был отсканирован
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if maze[y][x] == 2:  # Выход
                exit_rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
                exit_center = (x * cell_size + cell_size // 2, y * cell_size + cell_size // 2)
                
                for px, py, _ in white_points:
                    if math.dist((px, py), exit_center) < cell_size * 2:
                        pygame.draw.rect(screen, GREEN, exit_rect)
                        break
    
    # Рисуем направление игрока
    if not game_over:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        angle = math.atan2(mouse_y - player_pos[1], mouse_x - player_pos[0])
        tip_x = player_pos[0] + math.cos(angle) * player_radius * 1.5
        tip_y = player_pos[1] + math.sin(angle) * player_radius * 1.5
        left_x = player_pos[0] + math.cos(angle + math.pi * 0.75) * player_radius
        left_y = player_pos[1] + math.sin(angle + math.pi * 0.75) * player_radius
        right_x = player_pos[0] + math.cos(angle - math.pi * 0.75) * player_radius
        right_y = player_pos[1] + math.sin(angle - math.pi * 0.75) * player_radius
        pygame.draw.polygon(screen, BLUE, [(tip_x, tip_y), (left_x, left_y), (right_x, right_y)])
    
    # Кнопка перезапуска
    restart_rect = pygame.Rect(10, 10, 100, 30)
    pygame.draw.rect(screen, WHITE, restart_rect)
    font = pygame.font.SysFont(None, 24)
    restart_text = font.render("Restart", True, BLACK)
    screen.blit(restart_text, (restart_rect.centerx - restart_text.get_width() // 2, 
                              restart_rect.centery - restart_text.get_height() // 2))
    
    # Проверка клика по кнопке перезапуска
    if pygame.mouse.get_pressed()[0]:
        mouse_pos = pygame.mouse.get_pos()
        if restart_rect.collidepoint(mouse_pos):
            reset_game()
    
    # Сообщения
    if game_won:
        font = pygame.font.SysFont(None, 72)
        win_text = font.render("You Won!", True, GREEN)
        screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, 
                              HEIGHT // 2 - win_text.get_height() // 2))
    elif game_over:
        font = pygame.font.SysFont(None, 72)
        over_text = font.render("Game Over", True, RED)
        screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, 
                               HEIGHT // 2 - over_text.get_height() // 2))
    
    # Отображение cooldown для красного сканера
    if current_time - last_red_scan_time < red_scan_cooldown:
        cooldown_progress = (current_time - last_red_scan_time) / red_scan_cooldown
        pygame.draw.rect(screen, (50, 50, 50), (WIDTH - 120, 10, 100, 20))
        pygame.draw.rect(screen, RED, (WIDTH - 120, 10, int(100 * (1 - cooldown_progress)), 20))
        font = pygame.font.SysFont(None, 18)
        cooldown_text = font.render("Red Scanner", True, WHITE)
        screen.blit(cooldown_text, (WIDTH - 120, 32))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()