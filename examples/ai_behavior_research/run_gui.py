
"""
AI行为研究可视化界面启动脚本
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from examples.ai_behavior_research.game import test_game

if __name__ == "__main__":
    test_game(use_gui=True)

