import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
PLANET_RADIUS = 200
ROTATION_SPEED = 0.5

# Colors
SPACE_COLOR = (5, 5, 10)
OCEAN_COLOR = (20, 40, 100)

def generate_planet_texture(width, height):
    """Generates a seamless noise-like texture."""
    surf = pygame.Surface((width, height))
    surf.fill(OCEAN_COLOR)
    
    # Blobs
    num_blobs = 150
    for _ in range(num_blobs):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(10, 60)
        c_val = random.randint(50, 150)
        color = (c_val, c_val + 50, c_val)
        
        pygame.draw.circle(surf, color, (x, y), r)
        pygame.draw.circle(surf, color, (x - width, y), r)
        pygame.draw.circle(surf, color, (x + width, y), r)

    # Simple Ice caps
    pygame.draw.rect(surf, (200, 220, 255), (0, 0, width, 30))
    pygame.draw.rect(surf, (200, 220, 255), (0, height - 30, width, 30))

    return surf

def create_starfield(w, h, num_stars=150):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for _ in range(num_stars):
        x, y = random.randint(0, w), random.randint(0, h)
        b = random.randint(150, 255)
        pygame.draw.circle(s, (b, b, b), (x, y), 1)
    return s

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Spherical Projection Planet")
    clock = pygame.time.Clock()

    # Texture config
    tex_w, tex_h = 800, 400
    planet_texture = generate_planet_texture(tex_w, tex_h)
    
    # To handle wrapping, we create a double-wide texture
    wrapped_texture = pygame.Surface((tex_w * 2, tex_h))
    wrapped_texture.blit(planet_texture, (0, 0))
    wrapped_texture.blit(planet_texture, (tex_w, 0))

    stars = create_starfield(WIDTH, HEIGHT)

    # Lighting / Compositing layers
    # Sphere shading (Shadow)
    shadow_overlay = pygame.Surface((PLANET_RADIUS * 2, PLANET_RADIUS * 2), pygame.SRCALPHA)
    shadow_overlay.fill((0,0,0,0))
    
    # Procedural shadow generation
    # Iterate pixel by pixel for high quality alpha gradient shadow
    # This is slow, but we only do it once at startup
    for y in range(PLANET_RADIUS * 2):
        dy = (y - PLANET_RADIUS) / PLANET_RADIUS
        for x in range(PLANET_RADIUS * 2):
            dx = (x - PLANET_RADIUS) / PLANET_RADIUS
            if dx*dx + dy*dy <= 1.05: # radius margin
                # Simple dot product shading
                # Light coming from top-left (-1,-1)
                light_x, light_y = -0.707, -0.707
                dot = (dx * light_x + dy * light_y)
                
                # If dot is positive, it's lit (or partially lit)
                # If dot is negative, it's shadowed
                # We want full shadow at dot = -0.2 (terminator soft edge)
                
                # Shadow intensity: 0 (fully lit) to 255 (dark)
                # Map dot range [-1, 1] -> intensity
                # We want sharp terminator.
                # dot > 0.1 -> Intensity 0
                # dot < -0.1 -> Intensity 200
                
                intensity = 0
                if dot < 0.2:
                    val = (0.2 - dot) * 200
                    intensity = int(min(200, val))
                
                if intensity > 0:
                    shadow_overlay.set_at((x, y), (0, 0, 0, intensity))

    rotation_angle = 0.0

    # Settings for the Spherical Projection Grid
    SLICE_HEIGHT = 4         # Height of horizontal strips (Latitude resolution)
    LONGITUDE_SEGMENTS = 16   # Number of chunks per strip (Longitude resolution) 
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        rotation_angle += ROTATION_SPEED
        if rotation_angle >= 360: rotation_angle -= 360
        
        # Convert rotation to normalized texture X (0..1)
        # Texture width covers 360 degrees
        rot_norm = rotation_angle / 360.0

        screen.fill(SPACE_COLOR)
        screen.blit(stars, (0, 0))

        planet_center = (WIDTH // 2, HEIGHT // 2)
        
        # Draw the planet using horizontal slices
        # y_rel is relative to center
        for y_rel in range(-PLANET_RADIUS, PLANET_RADIUS, SLICE_HEIGHT):
            # 1. Determine spherical width at this latitude
            # Circle equation: x^2 + y^2 = r^2  -> x = sqrt(r^2 - y^2)
            # Use center of the slice for calculation
            y_center = y_rel + SLICE_HEIGHT / 2
            if abs(y_center) >= PLANET_RADIUS: continue # Skip edge cases

            half_width = math.sqrt(PLANET_RADIUS**2 - y_center**2)
            strip_width = int(half_width * 2)
            if strip_width <= 0: continue

            # 2. Determine texture Y coordinate (Latitude mapping)
            # y = R * sin(phi) -> phi = asin(y/R)
            # We map phi (-pi/2 to pi/2) to texture Y (height to 0)
            # Because texture usually has North (pi/2) at Y=0
            lat = math.asin(y_center / PLANET_RADIUS)
            
            # Map lat to 0..1
            # Lat: +1.57 (North) -> Tex Y: 0
            # Lat: -1.57 (South) -> Tex Y: 1
            norm_v = 1.0 - (lat + (math.pi/2)) / math.pi
            tex_y = int(norm_v * tex_h)
            tex_y = max(0, min(tex_h - 1, tex_y)) # Clamp

            # 3. Draw horizontal segments for this strip to simulate X-curvature
            # Visible longitude is -90 to +90 degrees relative to center normal
            
            # Segment step in radians
            segment_angle_step = (math.pi) / LONGITUDE_SEGMENTS # Pi radians total view
            
            # Base destination y on screen
            dest_y = (HEIGHT // 2) + y_rel
            
            for i in range(LONGITUDE_SEGMENTS):
                # Calculate angles for this segment (relative to center -pi/2 to pi/2)
                theta1 = - (math.pi / 2) + (i * segment_angle_step)
                theta2 = - (math.pi / 2) + ((i + 1) * segment_angle_step)
                
                # Project to Screen X
                # x = R_at_lat * sin(theta)
                x1 = half_width * math.sin(theta1)
                x2 = half_width * math.sin(theta2)
                
                seg_x = (WIDTH // 2) + int(x1)
                seg_w = int(x2 - x1)
                
                # To prevent gaps due to rounding, force min width
                if seg_w < 1: seg_w = 1 
                
                # Calculate Source Texture X
                # The visible face covers a specific range of U in the texture
                # Based on rotation.
                # theta is -pi/2..pi/2. Map to 0..0.5 in texture UV space (since 360 is full width)
                # But we need to add rotation offset.
                
                # Normalized longitude offset from 'center meridian'
                u1_local = (theta1 + (math.pi/2)) / (2 * math.pi) # 0 to 0.5
                u2_local = (theta2 + (math.pi/2)) / (2 * math.pi)
                
                # Add global rotation
                u1_final = (u1_local + rot_norm) % 1.0
                # u2 doesn't matter for start, we just calculate width of source
                u_width = (u2_local - u1_local)
                
                src_x = int(u1_final * tex_w)
                src_w = int(u_width * tex_w)
                
                dest_rect = pygame.Rect(seg_x, dest_y, seg_w + 1, SLICE_HEIGHT) # +1 to fill gaps
                
                # Extract and scale
                try:
                    # We assume texture Y is just 1px or 2px needed, but we used SLICE_HEIGHT
                    # to fill the screen gap.
                    # We take a small sample from texture (height 2) and stretch it to slice height
                    segment_img = wrapped_texture.subsurface((src_x, tex_y, src_w, 2))
                    segment_scaled = pygame.transform.scale(segment_img, (dest_rect.width, dest_rect.height))
                    screen.blit(segment_scaled, dest_rect)
                except ValueError:
                    pass

        # Draw overlays
        screen.blit(shadow_overlay, (planet_center[0] - PLANET_RADIUS, planet_center[1] - PLANET_RADIUS))
        
        # Rim (Atmosphere)
        pygame.draw.circle(screen, (100, 200, 255), planet_center, PLANET_RADIUS, 1)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
