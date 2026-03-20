"""AI队友行为树模块

包含AI队友实体、行为树控制器和战斗场景模拟器
"""

from .entities import Vector2, GameEntity, Character, Player, Enemy, Teammate
from .ai_behavior import AITeammate
from .simulator import BattleSimulator
from .config import GameConfig, PlayerConfig, TeammateConfig, EnemyConfig
from .score_manager import ScoreManager, ScoreEntry

__all__ = [
    'Vector2',
    'GameEntity',
    'Character',
    'Player',
    'Enemy',
    'Teammate',
    'AITeammate',
    'BattleSimulator',
    'GameConfig',
    'PlayerConfig',
    'TeammateConfig',
    'EnemyConfig',
    'ScoreManager',
    'ScoreEntry',
]
