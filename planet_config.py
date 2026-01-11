from dataclasses import dataclass

@dataclass
class PlanetConfig:
    radius: int = 50
    rotation_speed: float = 0.001
    weather_speed: float = 0.001
    
    # Colors
    c_ocean_deep: tuple = (35, 40, 80)
    c_ocean_shallow: tuple = (50, 80, 140)
    c_land_main: tuple = (100, 160, 60)
    c_land_highlight: tuple = (140, 200, 100)
    c_cloud: tuple = (230, 240, 255)
    
    # Terrain Generation
    num_islands: int = 12
    island_size_min: int = 20
    island_size_max: int = 100
    
    # Walker Gen
    walker_x_var: int = 4
    walker_y_var: int = 4
    
    # Clouds
    num_clouds: int = 15

# Presets

def get_terran_config():
    return PlanetConfig()

def get_ice_world_config():
    return PlanetConfig(
        c_ocean_deep=(20, 30, 60),
        c_ocean_shallow=(150, 200, 255),
        c_land_main=(200, 220, 255),
        c_land_highlight=(240, 250, 255),
        c_cloud=(200, 200, 220),
        num_islands=8,
        island_size_min=40,
        island_size_max=120,
        num_clouds=8
    )

def get_desert_config():
    return PlanetConfig(
        c_ocean_deep=(80, 40, 20),
        c_ocean_shallow=(140, 80, 40),
        c_land_main=(200, 140, 60),
        c_land_highlight=(230, 180, 100),
        c_cloud=(240, 220, 200),
        num_islands=20, # More scattered dunes/rocks
        island_size_min=10,
        island_size_max=40,
        num_clouds=5,
        weather_speed=0.003
    )

def get_toxic_config():
    return PlanetConfig(
        c_ocean_deep=(30, 10, 40),
        c_ocean_shallow=(60, 20, 80),
        c_land_main=(50, 120, 50),
        c_land_highlight=(100, 200, 50),
        c_cloud=(200, 100, 200), # Purple acid clouds
        rotation_speed=0.003,
        weather_speed=0.005,
        num_clouds=25
    )

def get_lava_config():
    return PlanetConfig(
        c_ocean_deep=(40, 5, 5), # Magma
        c_ocean_shallow=(180, 40, 10),
        c_land_main=(30, 20, 20), # Dark rock
        c_land_highlight=(60, 40, 40),
        c_cloud=(100, 100, 100), # Ash
        num_islands=6,
        weather_speed=0.004,
        num_clouds=20
    )

def get_gas_giant_config():
    return PlanetConfig(
        c_ocean_deep=(180, 160, 140), # Base tan
        c_ocean_shallow=(210, 180, 150), # Light band
        c_land_main=(160, 120, 100), # Darker band
        c_land_highlight=(140, 80, 60), # Great Red Spot colors
        c_cloud=(240, 230, 220), # Ammonia clouds
        rotation_speed=0.003,
        num_islands=40,
        island_size_min=30,
        island_size_max=80,
        walker_x_var=15, # Stretch horribly horizontally
        walker_y_var=1,  # Keep tight to bands
        num_clouds=20
    )

