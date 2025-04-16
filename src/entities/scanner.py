import pygame
import math
import random
from enum import Enum

class ScanType(Enum):
    WHITE = 1
    RED = 2

class Scanner:
    def __init__(self, config):
        self.config = config
        self.white_points = []
        self.red_points = []
        self.point_lifetime = 10000  # 10 seconds

    def white_scan(self, start_pos, target_pos, current_time):
        angle = math.atan2(target_pos[1] - start_pos[1], target_pos[0] - start_pos[0])
        points = []
        
        for _ in range(self.config.white_scan_points_per_frame):
            dist = random.uniform(0, self.config.scan_distance)
            end_x = start_pos[0] + math.cos(angle) * dist
            end_y = start_pos[1] + math.sin(angle) * dist
            points.append((end_x, end_y, current_time))
        
        return points

    def red_scan(self, start_pos, target_pos, current_time):
        main_angle = math.atan2(target_pos[1] - start_pos[1], target_pos[0] - start_pos[0])
        points = []
        
        for delta in range(-self.config.red_scan_angle_spread, 
                         self.config.red_scan_angle_spread + 1, 
                         self.config.red_scan_angle_step):
            angle = main_angle + math.radians(delta)
            dist = self.config.scan_distance
            end_x = start_pos[0] + math.cos(angle) * dist
            end_y = start_pos[1] + math.sin(angle) * dist
            points.append((end_x, end_y, current_time))
        
        return points

    def clean_old_points(self, current_time):
        self.white_points = [p for p in self.white_points if current_time - p[2] < self.point_lifetime]
        self.red_points = [p for p in self.red_points if current_time - p[2] < self.point_lifetime]