import pygame
import math
import random
from planet import Planet
from spaceship import Spaceship
from planet_config import (
    PlanetConfig, 
    get_terran_config, 
    get_ice_world_config, 
    get_desert_config, 
    get_toxic_config, 
    get_lava_config,
    get_gas_giant_config,
    get_sun_config
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
        get_lava_config(),
        get_gas_giant_config(),
        get_sun_config()
    ]
    p_config = random.choice(configs)
    
    # Apply global simulation overrides if needed, or stick to config defaults
    # p_config.rotation_speed = 0.001 
    
    current_planet = Planet(p_config)
    
    # Create Player
    # Start near the planet
    player = Spaceship(LOGICAL_WIDTH/2, LOGICAL_HEIGHT/2 - 80, LOGICAL_WIDTH, LOGICAL_HEIGHT)

    # Assets
    # Stars (Infinite field simulation)
    # Positions are relative to screen size (0..1) to be scaled by view
    stars = []
    for _ in range(80):
        x = random.uniform(0, LOGICAL_WIDTH)
        y = random.uniform(0, LOGICAL_HEIGHT)
        depth = 0.05 # Fixed depth so the star pattern doesn't distort (very distant)
        c = random.randint(100, 200)
        stars.append({'x': x, 'y': y, 'depth': depth, 'c': c})
    
    light_orbit_angle = 0.0
    
    # World Setup
    planet_pos = (LOGICAL_WIDTH/2, LOGICAL_HEIGHT/2)
    
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
        
        # Update Player
        player.handle_input()
        player.update()
        
        # Camera Update (Follow Player)
        # target_cam_x = player.pos.x - LOGICAL_WIDTH/2
        # target_cam_y = player.pos.y - LOGICAL_HEIGHT/2
        # For simplicity, rigid lock:
        camera_x = player.pos.x - LOGICAL_WIDTH / 2
        camera_y = player.pos.y - LOGICAL_HEIGHT / 2

        # Draw Background & Stars (Parallax)
        canvas.fill(C_SPACE)
        for s in stars:
            # Scroll stars based on depth
            # (Original Pos - Camera * Depth) % ScreenSize
            sx = (s['x'] - camera_x * s['depth']) % LOGICAL_WIDTH
            sy = (s['y'] - camera_y * s['depth']) % LOGICAL_HEIGHT
            
            ix, iy = int(sx), int(sy)
            if 0 <= ix < LOGICAL_WIDTH and 0 <= iy < LOGICAL_HEIGHT:
                 canvas.set_at((ix, iy), (s['c'], s['c'], s['c']))

        # Draw Planet (World Space -> Screen Space)
        # Planet is at planet_pos in world space
        screen_planet_x = int(planet_pos[0] - camera_x)
        screen_planet_y = int(planet_pos[1] - camera_y)
        
        # Only draw planet if somewhat on screen (Culling)
        # Dynamic margin based on radius
        planet_r = current_planet.radius
        margin = planet_r + 50
        
        if (-margin < screen_planet_x < LOGICAL_WIDTH + margin and 
            -margin < screen_planet_y < LOGICAL_HEIGHT + margin):
            current_planet.draw(canvas, screen_planet_x, screen_planet_y, light_vector)
        
        # Draw Player
        player.draw(canvas, camera_x, camera_y)
        
        # Scale to window
        scaled_surf = pygame.transform.scale(canvas, (WIDTH, HEIGHT))
        real_screen.blit(scaled_surf, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
