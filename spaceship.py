import pygame
import math

class Spaceship:
    def __init__(self, x, y, bounds_w, bounds_h):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.acc = pygame.math.Vector2(0, 0)
        self.angle = 90.0 # Degrees, 90 is UP usually in math standard if 0 is Right. 
                          # But we will handle logic explicitly.
        
        self.bounds_w = bounds_w
        self.bounds_h = bounds_h
        
        self.color = (255, 255, 240)
        self.thrust_power = 0.15
        self.friction = 0.96
        self.rotation_speed = 5.0
        
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Reset acceleration
        self.acc.x = 0
        self.acc.y = 0
        
        # Rotation (Left/Right)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle += self.rotation_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle -= self.rotation_speed
            
        # Thrust (Up/W)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            # Convert angle to vector
            # Assuming 0 is Right, 90 is Up
            rad = math.radians(self.angle)
            thrust_x = math.cos(rad) * self.thrust_power
            thrust_y = -math.sin(rad) * self.thrust_power # Y is down in screen coords
            
            self.acc.x = thrust_x
            self.acc.y = thrust_y

    def update(self):
        # Apply physics
        self.vel += self.acc
        self.vel *= self.friction
        self.pos += self.vel
        
        # No screen wrapping - infinite world
        # self.pos.x = self.pos.x % self.bounds_w
        # self.pos.y = self.pos.y % self.bounds_h

    def draw(self, surface, camera_x, camera_y):
        # Draw relative to camera
        ix = int(self.pos.x - camera_x)
        iy = int(self.pos.y - camera_y)
        
        # Draw simple dot for the ship body
        if 0 <= ix < self.bounds_w and 0 <= iy < self.bounds_h:
            pygame.draw.circle(surface, self.color, (ix, iy), 1)
        
            # Draw a tiny engine flare if thrusting? 
            # Or just a direction indicator (pixel)
            rad = math.radians(self.angle)
            front_x = ix + math.cos(rad) * 2
            front_y = iy - math.sin(rad) * 2
            
            # Draw a single pixel at the front to indicate direction
            if 0 <= front_x < self.bounds_w and 0 <= front_y < self.bounds_h:
                surface.set_at((int(front_x), int(front_y)), (200, 200, 200))
