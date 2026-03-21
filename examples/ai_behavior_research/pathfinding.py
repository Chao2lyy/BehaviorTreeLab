import heapq
from typing import List
from .entities import Vector2
from .grid_map import Grid


def manhattan_distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star(grid: Grid, start: tuple[int, int], goal: tuple[int, int]) -> List[tuple[int, int]]:
    open_set = []
    heapq.heappush(open_set, (0, 0, start))
    
    came_from = {}
    g_score = {start: 0}
    f_score = {start: manhattan_distance(start, goal)}
    
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                  (-1, -1), (-1, 1), (1, -1), (1, 1)]
    
    while open_set:
        current = heapq.heappop(open_set)[2]
        
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
        
        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)
            
            if not grid.is_walkable(neighbor[0], neighbor[1]):
                continue
            
            tentative_g_score = g_score[current] + 1
            
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + manhattan_distance(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], tentative_g_score, neighbor))
    
    return []


def find_path(grid: Grid, start_pos: Vector2, end_pos: Vector2) -> List[Vector2]:
    start_grid = grid.world_to_grid(start_pos)
    end_grid = grid.world_to_grid(end_pos)
    
    if not grid.is_walkable(start_grid[0], start_grid[1]) or not grid.is_walkable(end_grid[0], end_grid[1]):
        return []
    
    path_grid = a_star(grid, start_grid, end_grid)
    
    if not path_grid:
        return []
    
    path_world = [grid.grid_to_world(x, y) for x, y in path_grid]
    return path_world
