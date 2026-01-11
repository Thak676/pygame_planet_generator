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
ROTATION_SPEED = 1.0

# Colors (Pixel Art Palette)
C_SPACE = (20, 10, 25)
C_OCEAN_DEEP = (35, 40, 80)
C_OCEAN_SHALLOW = (50, 80, 140)
C_LAND_MAIN = (100, 160, 60)
C_LAND_HIGHLIGHT = (140, 200, 100)
C_CLOUD = (230, 240, 255)
C_SHADOW = (10, 5, 15)

def generate_pixel_texture(w, h):
    """Generates a chunky, pixel-art style map."""
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

    # 3. Clouds (Blobby shapes)
    num_clouds = 25
    for _ in range(num_clouds):
        cx = random.randint(0, w)
        cy = random.randint(0, h)
        
        # Build cloud out of multiple small puffs
        num_puffs = random.randint(4, 9)
        for _ in range(num_puffs):
            puff_w = random.randint(4, 9)
            puff_h = random.randint(2, 5)
            
            # Scatter puffs around center
            ox = random.randint(-8, 8)
            oy = random.randint(-3, 3)
            
            px, py = cx + ox, cy + oy
            
            # Draw puff
            pygame.draw.rect(surf, C_CLOUD, (px, py, puff_w, puff_h))
            
            # Handle wrapping for X axis
            if px < 0:
                pygame.draw.rect(surf, C_CLOUD, (px + w, py, puff_w, puff_h))
            elif px + puff_w > w:
                pygame.draw.rect(surf, C_CLOUD, (px - w, py, puff_w, puff_h))

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
    planet_texture = generate_pixel_texture(tex_w, tex_h)
    
    # Double width for easy wrapping
    wrapped_texture = pygame.Surface((tex_w * 2, tex_h))
    wrapped_texture.blit(planet_texture, (0, 0))
    wrapped_texture.blit(planet_texture, (tex_w, 0))

    # Assets
    # Stars (small points)
    stars_surf = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
    stars_surf.fill(C_SPACE)
    for _ in range(50):
        x, y = random.randint(0, LOGICAL_WIDTH), random.randint(0, LOGICAL_HEIGHT)
        c = random.randint(100, 200)
        stars_surf.set_at((x, y), (c, c, c))

    # Shadow with dithering feel
    # We build a shadow map where 0 = transparent, 1 = shadow
    # For pixel art, we often use DITHERING for shadow edges
    shadow_overlay = pygame.Surface((PLANET_RADIUS * 2, PLANET_RADIUS * 2), pygame.SRCALPHA)
    
    # 3D Light vector (Left, Top, Front)
    lx, ly, lz = -0.6, -0.4, 0.5
    mag = math.sqrt(lx*lx + ly*ly + lz*lz)
    lx, ly, lz = lx/mag, ly/mag, lz/mag

    for y in range(PLANET_RADIUS * 2):
        dy = (y - PLANET_RADIUS) / PLANET_RADIUS
        for x in range(PLANET_RADIUS * 2):
            dx = (x - PLANET_RADIUS) / PLANET_RADIUS
            dist_sq = dx*dx + dy*dy
            if dist_sq <= 1.0: # Inside circle
                # Calculate Z normal for curvature
                dz = math.sqrt(1.0 - dist_sq)
                
                # 3D Dot product
                dot = (dx * lx + dy * ly + dz * lz)
                
                # Multi-stage Dithering Layers
                # 1. Deep Shadow
                if dot < -0.2:
                    shadow_overlay.set_at((x, y), (0, 0, 0, 180))
                
                # 2. Medium Dither (Checkerboard) - The terminator curves due to dz
                elif dot < 0.05:
                    if (x + y) % 2 == 0:
                        shadow_overlay.set_at((x, y), (0, 0, 0, 180))
                
                # 3. Light Dither (Sparse) - Softens the edge further
                elif dot < 0.2:
                    if (x % 2 == 0) and (y % 2 == 0):
                         shadow_overlay.set_at((x, y), (0, 0, 0, 180))
    
    rotation_angle = 0.0

    # Rendering Config
    SLICE_HEIGHT = 2        # Use smaller strips for blockier look? Or 1 for precision
    # Actually, for pixel art look, we want crisp pixels.
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

        # Draw to canvas
        canvas.blit(stars_surf, (0, 0))

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
            # To simulate 3D rotation, we sample the texture at varying intervals
            # Center of planet = 1:1 texture scale (roughly)
            # Edge of planet = compressed
            
            # Optimization: Instead of drawing many small rects (which is slow in python loop),
            # construct a row surface by scaling a chunk of texture?
            # 
            # Yes: The visible arc represents 180 degrees (0.5 of texture width).
            # But it's projected non-linearly.
            # 
            # Simple "Old School" effect:
            # Just look up texture X for each screen X using asin
            
            dest_y = planet_center_y + y_rel
            start_x = planet_center_x - int(half_width)
            
            # This 'per-pixel' loop is dangerous in Python for performance if resolution is high.
            # But resolution is small (100px wide max). 100 * 100 = 10k iters per frame.
            # Should be fine for 30 FPS.
            
            # Current row in texture
            # We want to grab specific pixels from the texture row `tex_y`
            
            # Let's direct pixel access?
            # Pygame Surface access is slow. 
            # Better: Slice the texture row, scale it using a non-linear transform? 
            # No, standard transform is linear.
            
            # Let's try the segmented approach again, but cleaner.
            # Dynamic segmentation to fix "banding" artifacts
            # We ensure segments are roughly 2 pixels wide on screen for smoothness
            num_segments = max(16, width_here // 2)
            
            # Since theta steps are equal, the Source Texture Width is constant for all segments
            # (Visible face is 0.5 of texture width)
            # We calculate it once to avoid rounding jitter
            total_visible_tex_u = 0.5
            segment_tex_w = (total_visible_tex_u / num_segments) * tex_w
            
            # We boost width slightly to overlap seams (ceil-ish approach) or handled by scale
            # Using ceil(segment_tex_w) ensures we don't have gaps in texture reading, 
            # but scale might jitter.
            # Best to just integerize carefully loop-by-loop or use float fallback if pygame supported it.
            # We'll use round for x, and ceil for w.
            
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
                # We use the double-texture tech so we just modulo the start point
                src_x = int((u1 % 1.0) * tex_w)
                
                # Use calculated constant width for stability, but create int rect
                # Floating point accumulation might be an issue if we don't recalc u from i?
                # We recalc u from i every time, so no drift.
                src_w_pixels = int(segment_tex_w) + 1 # +1 for safety / overlap
                
                # Draw
                # subsurface(rect) -> scale -> blit
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
