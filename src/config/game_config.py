class GameConfig:
    def __init__(self):
        # Window settings
        self.width = 1000
        self.height = 800
        self.title = "2D Scanner Sombre"
        
        # Maze settings
        self.cell_size = 30
        self.wall_thickness = 2
        self.red_zone_percent = 0.3
        self.min_red_zone_distance_from_exit = 2
        
        # Player settings
        self.player_start_pos = (self.width//2, self.height//2)
        self.player_radius = 8
        self.player_speed = 4
        
        # Scanner settings
        self.scan_duration = 300  # ms
        self.red_scan_cooldown = 500  # ms
        self.scan_distance = 200
        self.white_scan_points_per_frame = 3
        self.red_scan_angle_spread = 45  # degrees
        self.red_scan_angle_step = 5  # degrees