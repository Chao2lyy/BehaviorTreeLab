from .config import MapConfig, GameConfig
from .entities import Vector2


class Grid:
    def __init__(self, config: MapConfig):
        self.config = config
        self.grid_width = int(config.map_width / config.grid_size)
        self.grid_height = int(config.map_height / config.grid_size)
        self.obstacles = set()
    
    def set_obstacle(self, grid_x: int, grid_y: int) -> None:
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            self.obstacles.add((grid_x, grid_y))
    
    def is_walkable(self, grid_x: int, grid_y: int) -> bool:
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            return (grid_x, grid_y) not in self.obstacles
        return False
    
    def world_to_grid(self, world_pos: Vector2) -> tuple[int, int]:
        grid_x = int(world_pos.x / self.config.grid_size)
        grid_y = int(world_pos.y / self.config.grid_size)
        return (grid_x, grid_y)
    
    def grid_to_world(self, grid_x: int, grid_y: int) -> Vector2:
        world_x = (grid_x + 0.5) * self.config.grid_size
        world_y = (grid_y + 0.5) * self.config.grid_size
        return Vector2(world_x, world_y)
    
    def create_sample_obstacles(self) -> None:
        for x in range(5, 10):
            self.set_obstacle(x, 5)
            self.set_obstacle(x, 6)
        for y in range(10, 15):
            self.set_obstacle(15, y)
            self.set_obstacle(16, y)
        self.set_obstacle(8, 12)
        self.set_obstacle(9, 12)
        self.set_obstacle(10, 12)
