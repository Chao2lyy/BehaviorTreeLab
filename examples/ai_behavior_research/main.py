"""
AI行为研究 - 主入口文件
展示FSM、行为树和Utility AI三种决策系统的行为差异
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pygame
import time
from typing import Optional
from examples.ai_behavior_research.config import GameConfig, NPCConfig, UtilityWeights
from examples.ai_behavior_research.game import Game


def run_game(
    use_gui: bool = True,
    num_frames: int = 1000,
    show_fps: bool = True,
    target_fps: int = 60
):
    """
    运行AI行为研究游戏
    
    Args:
        use_gui: 是否使用图形界面
        num_frames: 无头模式下运行的帧数
        show_fps: 是否显示FPS
        target_fps: 目标FPS
    """
    print("=" * 60)
    print("AI行为研究 - 三种决策系统对比")
    print("=" * 60)
    print("\nNPC配置:")
    print("  - FSM_NPC: 有限状态机，硬编码条件判断")
    print("  - BT_NPC: 行为树，树状结构决策")
    print("  - Utility_NPC: Utility AI，基于评分函数\n")
    
    config = GameConfig()
    
    print("游戏配置:")
    print(f"  - 地图大小: {config.map.map_width}x{config.map.map_height}")
    print(f"  - 目标FPS: {target_fps}")
    print()
    print("=" * 60)
    
    game = Game(config, use_gui=use_gui)
    game.spawn_interval = 200
    game.spawn_enemy()
    game.spawn_enemy()
    
    game.run(num_frames)
    
    print("\n" + "=" * 60)
    print("游戏结束")
    print("=" * 60)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI行为研究 - 三种决策系统对比")
    parser.add_argument(
        "--no-gui", 
        action="store_true", 
        help="使用无头模式运行（无图形界面）"
    )
    parser.add_argument(
        "--frames", 
        type=int, 
        default=1000, 
        help="无头模式下运行的帧数（默认: 1000）"
    )
    parser.add_argument(
        "--no-fps", 
        action="store_true", 
        help="不显示FPS信息"
    )
    parser.add_argument(
        "--target-fps", 
        type=int, 
        default=60, 
        help="目标FPS（默认: 60）"
    )
    
    args = parser.parse_args()
    
    run_game(
        use_gui=not args.no_gui,
        num_frames=args.frames,
        show_fps=not args.no_fps,
        target_fps=args.target_fps
    )
