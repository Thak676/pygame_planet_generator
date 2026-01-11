import pygame
import math
import random
from planet import Planet
from planet_config import (
    PlanetConfig, 
    get_terran_config, 
    get_ice_world_config, 
    get_desert_config, 
    get_toxic_config, 
    get_lava_config
)

# Initialize Pygame
pygame.init()

# Constants
SCALE_FACTOR = 4
LOGICAL_WIDTH, LOGICAL_HEIGHT = 200, 150
WIDTH, HEIGHT = LOGICAL_WIDTH * SCALE_FACTOR, LOGICAL_HEIGHT * SCALE_FACTOR
FPS = 30

# Simulation Constants (Universe)
ORBIT_SPEED = 0.0005
TRAVEL_SPEED = 0.2

# Colors
C_SPACE = (20, 10, 25)

def main():
    # Window setup
    real_screen = pygame.display.set_mode((WIDTH, HEIGHT))
    # Render surface (small)
    canvas = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    
    pygame.display.set_caption("Pixel Planet")
    clock = pygame.time.Clock()

    # Create Planet
    # Choose a random planet type
    configs = [
        get_terran_config(), 
        get_ice_world_config(), 
        get_desert_config(), 
        get_toxic_config(), 
        get_lava_config()
    ]
    p_config = random.choice(configs)
    
    # Apply global simulation overrides if needed, or stick to config defaults
    # p_config.rotation_speed = 0.001 
    
    current_planet = Planet(p_config)

    # Assets
    # Stars (small points)
    stars = []
    for _ in range(50):
        # Allow float for smooth movement
        x = float(random.randint(0, LOGICAL_WIDTH))
        y = float(random.randint(0, LOGICAL_HEIGHT))
        c = random.randint(100, 200)
        stars.append([x, y, c])
    
    light_orbit_angle = 0.0
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Dynamic Lighting / Orbit
        light_orbit_angle += ORBIT_SPEED
        lx = math.sin(light_orbit_angle)
        lz = math.cos(light_orbit_angle) 
        ly = -0.3 # Slight vertical tilt
        light_vector = (lx, ly, lz)

        # Update Planet
        current_planet.update()

        # Draw Background & Stars
        canvas.fill(C_SPACE)
        for s in stars:
            s[0] -= TRAVEL_SPEED
            if s[0] < 0: s[0] += LOGICAL_WIDTH
            
            ix, iy = int(s[0]), int(s[1])
            if 0 <= ix < LOGICAL_WIDTH and 0 <= iy < LOGICAL_HEIGHT:
                 canvas.set_at((ix, iy), (s[2], s[2], s[2]))

        # Draw Planet
        planet_center_x = LOGICAL_WIDTH // 2
        planet_center_y = LOGICAL_HEIGHT // 2
        current_planet.draw(canvas, planet_center_x, planet_center_y, light_vector)
        
        # Scale to window
        scaled_surf = pygame.transform.scale(canvas, (WIDTH, HEIGHT))
        real_screen.blit(scaled_surf, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
