from .config import GameConfig
from .entities import Vector2
from .grid_map import Grid
from .pathfinding import find_path


def main():
    print("=== 路径寻路系统测试 ===\n")
    
    config = GameConfig()
    grid = Grid(config.map)
    
    print("1. 创建示例障碍物...")
    grid.create_sample_obstacles()
    print(f"   障碍物数量: {len(grid.obstacles)}\n")
    
    start_pos = Vector2(50, 50)
    end_pos = Vector2(700, 550)
    
    print(f"2. 起点: {start_pos}")
    print(f"   终点: {end_pos}\n")
    
    print("3. 计算路径...")
    path = find_path(grid, start_pos, end_pos)
    
    if path:
        print(f"   ✓ 找到路径! 路径点数量: {len(path)}")
        print("   前5个路径点:")
        for i, point in enumerate(path[:5]):
            print(f"     {i+1}. {point}")
        if len(path) > 5:
            print("     ...")
    else:
        print("   ✗ 未找到可行路径")
    
    print("\n4. 测试被障碍物包围的情况...")
    obstacle_start = Vector2(5.5 * config.map.grid_size, 5.5 * config.map.grid_size)
    path_blocked = find_path(grid, obstacle_start, end_pos)
    
    if path_blocked:
        print(f"   ✓ 找到路径，共 {len(path_blocked)} 个路径点")
    else:
        print("   ✗ 正确: 起点在障碍物上，无可行路径")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    main()
