import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
SCALE_FACTOR = 4
LOGICAL_WIDTH, LOGICAL_HEIGHT = 200, 150
WIDTH, HEIGHT = LOGICAL_WIDTH * SCALE_FACTOR, LOGICAL_HEIGHT * SCALE_FACTOR
FPS = 30
PLANET_RADIUS = 50 
ROTATION_SPEED = 0.001
WEATHER_SPEED = 0.001
ORBIT_SPEED = 0.0005
TRAVEL_SPEED = 0.2

# Colors (Pixel Art Palette)
C_SPACE = (20, 10, 25)
C_OCEAN_DEEP = (35, 40, 80)
C_OCEAN_SHALLOW = (50, 80, 140)
C_LAND_MAIN = (100, 160, 60)
C_LAND_HIGHLIGHT = (140, 200, 100)
C_CLOUD = (230, 240, 255)
C_SHADOW = (10, 5, 15)

def generate_base_map(w, h):
    """Generates a chunky, pixel-art style map (Base Terrain)."""
    surf = pygame.Surface((w, h))
    surf.fill(C_OCEAN_DEEP)
    
    # generate "islands"
    # Create a few centers
    num_islands = 12
    centers = []
    for _ in range(num_islands):
        cx = random.randint(0, w)
        cy = random.randint(int(h*0.2), int(h*0.8))
        centers.append((cx, cy))
        
    # Walkers / Growth
    # For each pixel, if it's close to a center + noise, it's land
    # This is slow in python, so we paint using many small rects
    
    # 1. Base Land
    for cx, cy in centers:
        # Each island consists of many small blobs
        island_size = random.randint(20, 100)
        curr_x, curr_y = cx, cy
        for _ in range(island_size):
            # Draw a chunk
            chunk_w = random.randint(2, 6)
            chunk_h = random.randint(2, 6)
            
            # Shallow water halo
            pygame.draw.rect(surf, C_OCEAN_SHALLOW, (curr_x - 2, curr_y - 2, chunk_w + 4, chunk_h + 4))
            
            # Wrap around
            if curr_x < 0: pygame.draw.rect(surf, C_OCEAN_SHALLOW, (curr_x + w - 2, curr_y - 2, chunk_w + 4, chunk_h + 4))
            if curr_x > w: pygame.draw.rect(surf, C_OCEAN_SHALLOW, (curr_x - w - 2, curr_y - 2, chunk_w + 4, chunk_h + 4))

            # Move walker
            curr_x += random.randint(-4, 4)
            curr_y += random.randint(-4, 4)
            
    # 2. Main Land (Layer on top)
    for cx, cy in centers: # Reuse centers for consistency
        # Re-seed random or just use similar logic
        random.seed(cx * cy) 
        island_size = random.randint(20, 100)
        curr_x, curr_y = cx, cy
        for _ in range(island_size):
            chunk_w = random.randint(1, 4)
            chunk_h = random.randint(1, 4)
            
            col = C_LAND_MAIN
            if random.random() > 0.7: col = C_LAND_HIGHLIGHT
            
            pygame.draw.rect(surf, col, (curr_x, curr_y, chunk_w, chunk_h))
            
            # Wrap
            pygame.draw.rect(surf, col, (curr_x - w, curr_y, chunk_w, chunk_h))
            pygame.draw.rect(surf, col, (curr_x + w, curr_y, chunk_w, chunk_h))

            curr_x += random.randint(-3, 3)
            curr_y += random.randint(-3, 3)
    
    random.seed() # Reset seed
    return surf

class CloudManager:
    def __init__(self, w, h, num_clouds=15):
        self.w, self.h = w, h
        self.clouds = []
        for _ in range(num_clouds):
            self.create_cloud()

    def create_cloud(self):
        x = random.randint(0, self.w)
        y = random.randint(int(self.h * 0.1), int(self.h * 0.9))
        
        # Cloud composition
        puffs = []
        num_puffs = random.randint(5, 10)
        for _ in range(num_puffs):
            w = random.randint(4, 9)
            h = random.randint(2, 5)
            ox = random.randint(-8, 8)
            oy = random.randint(-4, 4)
            puffs.append({'ox': ox, 'oy': oy, 'w': w, 'h': h})
            
        self.clouds.append({
            'x': float(x),
            'y': float(y),
            'speed': WEATHER_SPEED + random.uniform(-0.05, 0.05),
            # Actually since rot speed is positive, we want clouds to move distinct from terrain.
            # Terrain moves because texture mapping u includes rot_norm.
            # So coordinate 0 on texture basically rotates around 360 over time.
            # Clouds at fixed X on texture rotate WITH the planet.
            # speed here is 'wind speed' relative to ground.
            'puffs': puffs
        })

    def update(self, rot_norm):
        # rot_norm (0..1) is the current rotation offset of the texture mapping.
        # The visible face of the planet roughly spans 0.5 (180 degrees) of the texture width.
        # Visible texture U range: [rot_norm, rot_norm + 0.5] (modulo 1.0).
        
        # Define the "Safe Zone" where clouds are visible or near-visible.
        # We add padding to ensure we don't mutate clouds right at the edge of the screen.
        safe_u_start = (rot_norm - 0.2) % 1.0
        safe_u_end = (rot_norm + 0.7) % 1.0 
        
        safe_x_start = safe_u_start * self.w
        safe_x_end = safe_u_end * self.w
        
        is_split_safety = safe_x_end < safe_x_start

        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        
        for c in self.clouds:
            # Move cloud (Float precision for smoothness)
            c['x'] += c['speed']
            if c['x'] >= self.w:
                 c['x'] -= self.w
            
            # Check visibility / safety
            cx = c['x']
            in_safe_zone = False
            
            if not is_split_safety:
                if safe_x_start <= cx <= safe_x_end:
                    in_safe_zone = True
            else:
                # Wrap case
                if cx >= safe_x_start or cx <= safe_x_end:
                    in_safe_zone = True
            
            # If NOT in safe zone (deep in the back), mutate shape slightly
            if not in_safe_zone:
                # Mutation (Evolution)
                if random.random() < 0.1:
                    if c['puffs']:
                        p = random.choice(c['puffs'])
                        # Jitter
                        p['ox'] += random.uniform(-0.5, 0.5)
                        p['oy'] += random.uniform(-0.5, 0.5)
                        
                        # Clamp
                        p['ox'] = max(-12, min(12, p['ox']))
                        p['oy'] = max(-6, min(6, p['oy']))

                    # Add/Remove puffs
                    if random.random() < 0.02 and len(c['puffs']) < 15:
                        c['puffs'].append({
                            'ox': random.randint(-8, 8), 
                            'oy': random.randint(-4, 4), 
                            'w': random.randint(3, 7), 
                            'h': random.randint(2, 4)
                        })
                    if random.random() < 0.02 and len(c['puffs']) > 4:
                        c['puffs'].pop()

            # Draw using floats (Pygame will handle sub-pixel truncating, avoiding int() snap artifacts)
            positions = [cx, cx - self.w, cx + self.w]
            for dx in positions:
                # Cull drawing for performance/sanity
                if -30 < dx < self.w + 30:
                     for p in c['puffs']:
                         pygame.draw.rect(surf, C_CLOUD, (dx + p['ox'], c['y'] + p['oy'], p['w'], p['h']))

        return surf

def create_dither_pattern(w, h):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(0, h, 2):
        for x in range(0, w, 2):
             if (x + y) % 2 == 0:
                 s.set_at((x, y), (0, 0, 0, 50))
    return s

def main():
    # Window setup
    real_screen = pygame.display.set_mode((WIDTH, HEIGHT))
    # Render surface (small)
    canvas = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    
    pygame.display.set_caption("Pixel Planet")
    clock = pygame.time.Clock()

    # Texture
    tex_w, tex_h = 256, 128
    base_texture = generate_base_map(tex_w, tex_h)
    clouds = CloudManager(tex_w, tex_h)
    
    # Double width for easy wrapping
    wrapped_texture = pygame.Surface((tex_w * 2, tex_h))

    # Assets
    # Stars (small points)
    stars = []
    for _ in range(50):
        # Allow float for smooth movement
        x = float(random.randint(0, LOGICAL_WIDTH))
        y = float(random.randint(0, LOGICAL_HEIGHT))
        c = random.randint(100, 200)
        stars.append([x, y, c])

    # Shadow Pre-calculation
    # We store valid pixels to avoid iterating the whole square every frame
    pixel_normals = []
    for y in range(PLANET_RADIUS * 2):
        dy = (y - PLANET_RADIUS) / PLANET_RADIUS
        for x in range(PLANET_RADIUS * 2):
            dx = (x - PLANET_RADIUS) / PLANET_RADIUS
            dist_sq = dx*dx + dy*dy
            if dist_sq <= 1.0:
                dz = math.sqrt(1.0 - dist_sq)
                pixel_normals.append((x, y, dx, dy, dz))

    shadow_overlay = pygame.Surface((PLANET_RADIUS * 2, PLANET_RADIUS * 2), pygame.SRCALPHA)
    
    rotation_angle = 0.0
    light_orbit_angle = 0.0

    # Rendering Config
    # 1px slice height ensures specific rows.
    SLICE_HEIGHT = 1 
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        rotation_angle += ROTATION_SPEED
        if rotation_angle >= 360: rotation_angle -= 360
        
        rot_norm = rotation_angle / 360.0

        # Dynamic Lighting
        light_orbit_angle += ORBIT_SPEED # Slower day/night cycle
        # Orbit the light around the planet
        lx = math.sin(light_orbit_angle)
        lz = math.cos(light_orbit_angle) 
        ly = -0.3 # Slight vertical tilt
        
        # Update Clouds
        # We pass rotation_angle or rot_norm to help it know what's visible
        cloud_surf = clouds.update(rot_norm) # Pass rot_norm to check visibility
        
        # Composite Texture
        # Combine terrain + clouds
        planet_texture = base_texture.copy()
        planet_texture.blit(cloud_surf, (0, 0))
        
        # Update the wrapped texture buffer used by the renderer
        wrapped_texture.blit(planet_texture, (0, 0))
        wrapped_texture.blit(planet_texture, (tex_w, 0))
        
        # Re-render shadow
        shadow_overlay.fill((0,0,0,0))
        
        for x, y, nx, ny, nz in pixel_normals:
             # Dot product
             dot = nx * lx + ny * ly + nz * lz
             
             # Shadow Logic:
             # dot < 0 means surface faces away from light -> Full Shadow (Darkest)
             # This ensures exactly half the planet is in the "darkest shade"
             if dot < 0.0:
                 shadow_overlay.set_at((x, y), (0, 0, 0, 180))
             # Dither bands appear on the LIT side as light fades (grazing angle)
             elif dot < 0.15:
                 if (x + y) % 2 == 0:
                     shadow_overlay.set_at((x, y), (0, 0, 0, 180))
             elif dot < 0.3:
                 if (x % 2 == 0) and (y % 2 == 0):
                      shadow_overlay.set_at((x, y), (0, 0, 0, 180))

        # Draw Background & Stars
        canvas.fill(C_SPACE)
        for s in stars:
            s[0] -= TRAVEL_SPEED
            if s[0] < 0: s[0] += LOGICAL_WIDTH
            
            ix, iy = int(s[0]), int(s[1])
            # Basic clipping check
            if 0 <= ix < LOGICAL_WIDTH and 0 <= iy < LOGICAL_HEIGHT:
                 canvas.set_at((ix, iy), (s[2], s[2], s[2]))

        planet_center_x = LOGICAL_WIDTH // 2
        planet_center_y = LOGICAL_HEIGHT // 2
        
        # --- Planet Rendering ---
        # Iterate rows
        for y_rel in range(-PLANET_RADIUS, PLANET_RADIUS, SLICE_HEIGHT):
            y_center = y_rel
            if abs(y_center) >= PLANET_RADIUS: continue

            # Circle width at this Y
            half_width = math.sqrt(PLANET_RADIUS**2 - y_center**2)
            width_here = int(half_width * 2)
            if width_here <= 0: continue

            # Lat coordinate
            lat = math.asin(y_center / PLANET_RADIUS)
            norm_v = 1.0 - (lat + (math.pi/2)) / math.pi
            tex_y = int(norm_v * tex_h)
            tex_y = max(0, min(tex_h-1, tex_y))

            # Draw row
            dest_y = planet_center_y + y_rel
            start_x = planet_center_x - int(half_width)
            
            # Dynamic segmentation to fix "banding" artifacts
            # We ensure segments are roughly 2 pixels wide on screen for smoothness
            num_segments = max(16, width_here // 2)
            
            total_visible_tex_u = 0.5
            segment_tex_w = (total_visible_tex_u / num_segments) * tex_w
            
            for i in range(num_segments):
                # Screen space segments (linear in angle)
                t1 = - (math.pi / 2) + (i * (math.pi/num_segments))
                t2 = - (math.pi / 2) + ((i + 1) * (math.pi/num_segments))
                
                # Projected widths
                x1 = half_width * math.sin(t1)
                x2 = half_width * math.sin(t2)
                
                seg_x = int(start_x + half_width + x1)
                seg_w = int(start_x + half_width + x2) - seg_x
                
                if seg_w < 1: seg_w = 1
                
                # Texture UVs
                # Look up start U
                u1 = (t1 + math.pi/2) / (2*math.pi) + rot_norm
                
                # Calculate pixel X in texture (wrapped)
                src_x = int((u1 % 1.0) * tex_w)
                src_w_pixels = int(segment_tex_w) + 1 
                
                # Draw
                try:
                    chunk = wrapped_texture.subsurface((src_x, tex_y, src_w_pixels, 1))
                    chunk = pygame.transform.scale(chunk, (seg_w, 1))
                    canvas.blit(chunk, (seg_x, dest_y))
                except (ValueError, pygame.error):
                    pass

        # Apply Shadow
        canvas.blit(shadow_overlay, (planet_center_x - PLANET_RADIUS, planet_center_y - PLANET_RADIUS))
        
        # Scale to window
        scaled_surf = pygame.transform.scale(canvas, (WIDTH, HEIGHT))
        real_screen.blit(scaled_surf, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
