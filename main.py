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

    # Create Solar System
    # Sun at (0,0)
    sun_config = get_sun_config()
    sun = Planet(sun_config)
    
    # Orbiting Planets
    planets = []
    
    # Types of planets to spawn (Config, Distance Multiplier relative to Sun radius)
    planet_types = [
        (get_lava_config(), 2.0),
        (get_terran_config(), 3.5),
        (get_gas_giant_config(), 6.0),
        (get_ice_world_config(), 8.5)
    ]
    
    # Base distance to ensure we don't clip inside the sun
    orbit_base = sun.radius + 150
    
    for config, dist_mult in planet_types:
        d = int(orbit_base * dist_mult)
        # Kepler-ish orbital speed (slower further out)
        # Made extremely slow (0.5 -> 0.02)
        speed = 0.0002 / math.sqrt(d) 
        angle = random.uniform(0, 6.28)
        
        planets.append({
            'body': Planet(config),
            'dist': d,
            'speed': speed,
            'angle': angle,
            'x': 0, 'y': 0
        })

    # Create Player
    # Start near the Terran planet (index 1)
    start_p = planets[1]
    # Offset slightly so player sees the planet
    start_x = math.cos(start_p['angle']) * (start_p['dist'] + 80)
    start_y = math.sin(start_p['angle']) * (start_p['dist'] + 80)
    
    player = Spaceship(start_x, start_y, LOGICAL_WIDTH, LOGICAL_HEIGHT)

    # Assets
    # Stars (Infinite field simulation)
    stars = []
    for _ in range(80):
        x = random.uniform(0, LOGICAL_WIDTH)
        y = random.uniform(0, LOGICAL_HEIGHT)
        depth = 0.05 
        c = random.randint(100, 200)
        stars.append({'x': x, 'y': y, 'depth': depth, 'c': c})
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update Sun
        sun.update()
        
        # Update Planets
        for p in planets:
            p['angle'] += p['speed']
            p['x'] = math.cos(p['angle']) * p['dist']
            p['y'] = math.sin(p['angle']) * p['dist']
            p['body'].update()
        
        # Update Player
        player.handle_input()
        player.update()
        
        # Camera Update (Rigid Lock)
        camera_x = player.pos.x - LOGICAL_WIDTH / 2
        camera_y = player.pos.y - LOGICAL_HEIGHT / 2

        # Draw Background & Stars (Parallax)
        canvas.fill(C_SPACE)
        for s in stars:
            # Scroll stars based on depth
            sx = (s['x'] - camera_x * s['depth']) % LOGICAL_WIDTH
            sy = (s['y'] - camera_y * s['depth']) % LOGICAL_HEIGHT
            
            ix, iy = int(sx), int(sy)
            if 0 <= ix < LOGICAL_WIDTH and 0 <= iy < LOGICAL_HEIGHT:
                 canvas.set_at((ix, iy), (s['c'], s['c'], s['c']))

        # Draw Sun
        sun_sc_x = int(0 - camera_x)
        sun_sc_y = int(0 - camera_y)
        sun_margin = sun.radius + 50
        
        if (-sun_margin < sun_sc_x < LOGICAL_WIDTH + sun_margin and 
            -sun_margin < sun_sc_y < LOGICAL_HEIGHT + sun_margin):
            # Sun looks fine with simple front lighting or no lighting
            sun.draw(canvas, sun_sc_x, sun_sc_y, (0, 0, 1))

        # Draw Planets
        for p in planets:
            px, py = p['x'], p['y']
            sc_x = int(px - camera_x)
            sc_y = int(py - camera_y)
            
            radius = p['body'].radius
            margin = radius + 50
            
            if (-margin < sc_x < LOGICAL_WIDTH + margin and 
                -margin < sc_y < LOGICAL_HEIGHT + margin):
                
                # Calculate light direction (from planet TO sun)
                # Sun is at 0,0
                dx, dy = -px, -py
                dist = math.sqrt(dx*dx + dy*dy)
                
                lx, ly, lz = 0, 0, 1
                if dist > 0:
                    lx = dx / dist
                    ly = dy / dist
                    # Add a small Z component so the center isn't pitch black
                    lz = 0.25 
                
                p['body'].draw(canvas, sc_x, sc_y, (lx, ly, lz))
        
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
