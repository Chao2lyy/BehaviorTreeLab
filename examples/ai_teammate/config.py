"""游戏配置类"""

from dataclasses import dataclass


@dataclass
class PlayerConfig:
    """玩家配置"""
    max_hp: float = 100.0
    speed: float = 4.0
    attack_damage: float = 20.0
    attack_range: float = 80.0
    attack_cooldown: int = 30


@dataclass
class TeammateConfig:
    """AI队友配置"""
    max_hp: float = 100.0
    speed: float = 2.5
    melee_damage: float = 15.0
    ranged_damage: float = 10.0
    melee_cooldown: int = 45
    ranged_cooldown: int = 60
    healing_potion_count: int = 3
    detection_range: float = 200.0
    melee_range: float = 80.0
    follow_distance: float = 100.0
    low_hp_threshold: float = 0.3
    behavior_priority: list = None
    
    def __post_init__(self):
        if self.behavior_priority is None:
            self.behavior_priority = ['emergency', 'combat', 'follow', 'idle']


@dataclass
class EnemyConfig:
    """敌人配置"""
    max_hp: float = 80.0
    speed: float = 1.5
    attack_damage: float = 10.0
    attack_range: float = 60.0
    attack_cooldown: int = 60


@dataclass
class SpawnConfig:
    """敌人生成配置"""
    max_enemies: int = 6
    spawn_interval: int = 180
    min_spawn_x: float = 50.0
    max_spawn_x: float = 700.0
    min_spawn_y: float = 50.0
    max_spawn_y: float = 650.0


@dataclass
class HealthPackConfig:
    """血包配置"""
    heal_amount: float = 30.0
    spawn_chance: float = 0.01
    max_packs: int = 3
    pickup_range: float = 40.0


@dataclass
class ScoreConfig:
    """分数配置"""
    player_kill_score: int = 100
    teammate_kill_score: int = 50
    max_score_history: int = 10


class GameConfig:
    """游戏总配置"""
    
    def __init__(self):
        """初始化游戏配置"""
        self.player = PlayerConfig()
        self.teammate = TeammateConfig()
        self.enemy = EnemyConfig()
        self.spawn = SpawnConfig()
        self.health_pack = HealthPackConfig()
        self.score = ScoreConfig()
