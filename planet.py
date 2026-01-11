import pygame
import math
import random
from planet_config import PlanetConfig

class CloudManager:
    def __init__(self, w, h, speed_base, color, num_clouds=15):
        self.w, self.h = w, h
        self.speed_base = speed_base
        self.color = color
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
            'speed': self.speed_base + random.uniform(-0.05, 0.05),
            'puffs': puffs
        })

    def update(self, rot_norm):
        # rot_norm (0..1) is the current rotation offset of the texture mapping.
        # Define the "Safe Zone" where clouds are visible or near-visible.
        safe_u_start = (rot_norm - 0.2) % 1.0
        safe_u_end = (rot_norm + 0.7) % 1.0 
        
        safe_x_start = safe_u_start * self.w
        safe_x_end = safe_u_end * self.w
        
        is_split_safety = safe_x_end < safe_x_start

        surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        
        for c in self.clouds:
            # Move cloud
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

            # Draw using floats
            positions = [cx, cx - self.w, cx + self.w]
            for dx in positions:
                # Cull drawing for performance/sanity
                if -30 < dx < self.w + 30:
                     for p in c['puffs']:
                         pygame.draw.rect(surf, self.color, (dx + p['ox'], c['y'] + p['oy'], p['w'], p['h']))

        return surf

class Planet:
    def __init__(self, config: PlanetConfig):
        self.config = config
        self.radius = config.radius
        self.rotation_speed = config.rotation_speed
        self.rotation_angle = 0.0
        
        # Texture Size
        self.tex_w = 256
        self.tex_h = 128
        
        # Generate Terrain
        self.base_texture = self.generate_base_map(self.tex_w, self.tex_h)
        self.wrapped_texture = pygame.Surface((self.tex_w * 2, self.tex_h))
        
        # Weather
        self.clouds = CloudManager(self.tex_w, self.tex_h, config.weather_speed, config.c_cloud, config.num_clouds)
        
        # Pre-calc 3D Normals
        self.pixel_normals = []
        for y in range(self.radius * 2):
            dy = (y - self.radius) / self.radius
            for x in range(self.radius * 2):
                dx = (x - self.radius) / self.radius
                dist_sq = dx*dx + dy*dy
                if dist_sq <= 1.0:
                    dz = math.sqrt(1.0 - dist_sq)
                    self.pixel_normals.append((x, y, dx, dy, dz))

        self.shadow_overlay = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)

    def generate_base_map(self, w, h):
        # Helper to add slight noise to colors
        def vary_color(color, amount=10):
            r, g, b = color
            r = max(0, min(255, r + random.randint(-amount, amount)))
            g = max(0, min(255, g + random.randint(-amount, amount)))
            b = max(0, min(255, b + random.randint(-amount, amount)))
            return (r, g, b)

        surf = pygame.Surface((w, h))
        surf.fill(self.config.c_ocean_deep)
        
        num_islands = self.config.num_islands
        centers = []
        for _ in range(num_islands):
            cx = random.randint(0, w)
            cy = random.randint(int(h*0.2), int(h*0.8))
            centers.append((cx, cy))
            
        # 1. Base Land
        for cx, cy in centers:
            island_size = random.randint(self.config.island_size_min, self.config.island_size_max)
            curr_x, curr_y = cx, cy
            for _ in range(island_size):
                chunk_w = random.randint(2, 6)
                chunk_h = random.randint(2, 6)
                
                col = vary_color(self.config.c_ocean_shallow)
                
                pygame.draw.rect(surf, col, (curr_x - 2, curr_y - 2, chunk_w + 4, chunk_h + 4))
                if curr_x < 0: pygame.draw.rect(surf, col, (curr_x + w - 2, curr_y - 2, chunk_w + 4, chunk_h + 4))
                if curr_x > w: pygame.draw.rect(surf, col, (curr_x - w - 2, curr_y - 2, chunk_w + 4, chunk_h + 4))
                curr_x += random.randint(-self.config.walker_x_var, self.config.walker_x_var)
                curr_y += random.randint(-self.config.walker_y_var, self.config.walker_y_var)
                
        # 2. Main Land
        for cx, cy in centers: 
            random.seed(cx * cy) 
            island_size = random.randint(self.config.island_size_min, self.config.island_size_max)
            curr_x, curr_y = cx, cy
            for _ in range(island_size):
                chunk_w = random.randint(1, 4)
                chunk_h = random.randint(1, 4)
                
                base_col = self.config.c_land_main
                if random.random() > 0.7: base_col = self.config.c_land_highlight
                
                col = vary_color(base_col)
                
                pygame.draw.rect(surf, col, (curr_x, curr_y, chunk_w, chunk_h))
                pygame.draw.rect(surf, col, (curr_x - w, curr_y, chunk_w, chunk_h))
                pygame.draw.rect(surf, col, (curr_x + w, curr_y, chunk_w, chunk_h))
                curr_x += random.randint(-self.config.walker_x_var, self.config.walker_x_var)
                curr_y += random.randint(-self.config.walker_y_var, self.config.walker_y_var)
        random.seed() 
        return surf

    def update(self):
        self.rotation_angle += self.rotation_speed
        if self.rotation_angle >= 360: self.rotation_angle -= 360
        
        rot_norm = self.rotation_angle / 360.0
        
        cloud_surf = self.clouds.update(rot_norm)
        
        planet_texture = self.base_texture.copy()
        planet_texture.blit(cloud_surf, (0, 0))
        
        self.wrapped_texture.blit(planet_texture, (0, 0))
        self.wrapped_texture.blit(planet_texture, (self.tex_w, 0))

    def draw(self, surface, center_x, center_y, light_vector):
        lx, ly, lz = light_vector
        
        # Update Shadow
        self.shadow_overlay.fill((0,0,0,0))
        for x, y, nx, ny, nz in self.pixel_normals:
             dot = nx * lx + ny * ly + nz * lz
             if dot < 0.0:
                 self.shadow_overlay.set_at((x, y), (0, 0, 0, 180))
             elif dot < 0.15:
                 if (x + y) % 2 == 0:
                     self.shadow_overlay.set_at((x, y), (0, 0, 0, 180))
             elif dot < 0.3:
                 if (x % 2 == 0) and (y % 2 == 0):
                      self.shadow_overlay.set_at((x, y), (0, 0, 0, 180))

        # Spherical Projection
        slice_height = 1
        rot_norm = self.rotation_angle / 360.0
        
        for y_rel in range(-self.radius, self.radius, slice_height):
            y_center = y_rel
            if abs(y_center) >= self.radius: continue

            # Circle width at this Y
            half_width = math.sqrt(self.radius**2 - y_center**2)
            width_here = int(half_width * 2)
            if width_here <= 0: continue

            # Lat coordinate
            lat = math.asin(y_center / self.radius)
            norm_v = 1.0 - (lat + (math.pi/2)) / math.pi
            tex_y = int(norm_v * self.tex_h)
            tex_y = max(0, min(self.tex_h-1, tex_y))

            # Draw row
            dest_y = center_y + y_rel
            start_x = center_x - int(half_width)
            
            num_segments = max(16, width_here // 2)
            
            total_visible_tex_u = 0.5
            segment_tex_w = (total_visible_tex_u / num_segments) * self.tex_w
            
            for i in range(num_segments):
                # Screen space segments
                t1 = - (math.pi / 2) + (i * (math.pi/num_segments))
                t2 = - (math.pi / 2) + ((i + 1) * (math.pi/num_segments))
                
                x1 = half_width * math.sin(t1)
                x2 = half_width * math.sin(t2)
                
                seg_x = int(start_x + half_width + x1)
                seg_w = int(start_x + half_width + x2) - seg_x
                
                if seg_w < 1: seg_w = 1
                
                # Texture UVs
                u1 = (t1 + math.pi/2) / (2*math.pi) + rot_norm
                
                src_x = int((u1 % 1.0) * self.tex_w)
                src_w_pixels = int(segment_tex_w) + 1 
                
                try:
                    chunk = self.wrapped_texture.subsurface((src_x, tex_y, src_w_pixels, 1))
                    chunk = pygame.transform.scale(chunk, (seg_w, 1))
                    surface.blit(chunk, (seg_x, dest_y))
                except (ValueError, pygame.error):
                    pass

        # Apply Shadow
        surface.blit(self.shadow_overlay, (center_x - self.radius, center_y - self.radius))
