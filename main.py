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
WIDTH, HEIGHT = 1920, 1080 
FPS = 30

# Simulation Constants (Universe)
ORBIT_SPEED = 0.0005
TRAVEL_SPEED = 0.2

# Colors
C_SPACE = (20, 10, 25)

def main():
    # Window setup
    real_screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pixel Planet")
    clock = pygame.time.Clock()

    # Zoom / Scale State
    current_scale = 4.0
    
    def get_logical_dims(scale):
        return int(WIDTH / scale), int(HEIGHT / scale)

    logical_w, logical_h = get_logical_dims(current_scale)
    canvas = pygame.Surface((logical_w, logical_h))

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
        speed = 0.02 / math.sqrt(d) 
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
    
    player = Spaceship(start_x, start_y, logical_w, logical_h)

    # Assets
    # Stars (Infinite field simulation)
    stars = []
    
    def refresh_stars(w, h, cam_x, cam_y):
        # When zooming, we want to somewhat preserve the starfield feel or just regen
        # For simplicity, regen full field based on density
        stars.clear()
        num_stars = int(w * h * 0.0008) 
        for _ in range(num_stars):
            # Generate relative to camera so we are in a populated area
            x = random.uniform(cam_x, cam_x + w)
            y = random.uniform(cam_y, cam_y + h)
            depth = 0.05 
            c = random.randint(100, 200)
            stars.append({'x': x, 'y': y, 'depth': depth, 'c': c})

    # Initial stars: assume camera at 0? No, player pos
    # Camera calc
    cam_x = player.pos.x - logical_w / 2
    cam_y = player.pos.y - logical_h / 2
    refresh_stars(logical_w, logical_h, cam_x, cam_y)
    
    light_orbit_angle = 0.0
    
    running = True
    while running:
        # Camera calc for this frame (needed for input/stars logic?)
        # We calculate it before drawing usually, but let's have a current val
        camera_x = player.pos.x - logical_w / 2
        camera_y = player.pos.y - logical_h / 2

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                old_scale = current_scale
                # Mouse wheel up (positive) -> Zoom IN (increase scale)
                # Mouse wheel down (negative) -> Zoom OUT (decrease scale)
                current_scale += event.y * 0.2
                current_scale = max(0.5, min(current_scale, 8.0))
                
                if abs(current_scale - old_scale) > 0.01:
                    logical_w, logical_h = get_logical_dims(current_scale)
                    canvas = pygame.Surface((logical_w, logical_h))
                    
                    # Update Player Culling Bounds
                    player.bounds_w = logical_w
                    player.bounds_h = logical_h
                    
                    # Refresh stars for new viewport size 
                    # (centered around current camera to avoid empty voids immediately)
                    # Recalc camera for new center
                    new_cam_x = player.pos.x - logical_w / 2
                    new_cam_y = player.pos.y - logical_h / 2
                    refresh_stars(logical_w, logical_h, new_cam_x, new_cam_y)
                    
                    # Update camera var for this frame immediately
                    camera_x = new_cam_x
                    camera_y = new_cam_y

        # Dynamic Lighting / Orbit
        light_orbit_angle += ORBIT_SPEED
        lx = math.sin(light_orbit_angle)
        lz = math.cos(light_orbit_angle) 
        ly = -0.3 # Slight vertical tilt
        light_vector = (lx, ly, lz)

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
        camera_x = player.pos.x - logical_w / 2
        camera_y = player.pos.y - logical_h / 2

        # Draw Background & Stars (Parallax)
        canvas.fill(C_SPACE)
        for s in stars:
            # Scroll stars based on depth
            # (Original World Pos - Camera * Depth) % ScreenSize
            # Note: With resizing screen, mod logic is tricky. 
            # We switched to "world space stars" in refresh_stars but simple parallax needs a wrap.
            # Let's simple wrap:
            sx = (s['x'] - camera_x * s['depth']) % logical_w
            sy = (s['y'] - camera_y * s['depth']) % logical_h
            
            ix, iy = int(sx), int(sy)
            if 0 <= ix < logical_w and 0 <= iy < logical_h:
                 canvas.set_at((ix, iy), (s['c'], s['c'], s['c']))

        # Draw Sun
        sun_sc_x = int(0 - camera_x)
        sun_sc_y = int(0 - camera_y)
        sun_margin = sun.radius + 50
        
        if (-sun_margin < sun_sc_x < logical_w + sun_margin and 
            -sun_margin < sun_sc_y < logical_h + sun_margin):
            # Sun looks fine with simple front lighting or no lighting
            sun.draw(canvas, sun_sc_x, sun_sc_y, (0, 0, 1))

        # Draw Planets
        for p in planets:
            px, py = p['x'], p['y']
            sc_x = int(px - camera_x)
            sc_y = int(py - camera_y)
            
            radius = p['body'].radius
            margin = radius + 50
            
            if (-margin < sc_x < logical_w + margin and 
                -margin < sc_y < logical_h + margin):
                
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
