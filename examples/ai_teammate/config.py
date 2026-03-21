"""游戏配置类"""

from dataclasses import dataclass
from typing import List


@dataclass
class SkillConfig:
    """技能配置"""
    
    bullet_damage: float = 10.0
    """子弹技能基础伤害值"""
    
    bullet_speed: float = 8.0
    """子弹飞行速度（像素/帧）"""
    
    bullet_fire_rate: int = 60
    """子弹发射间隔（帧数，60帧约等于1秒）"""
    
    bullet_count: int = 1
    """每次发射的子弹数量"""
    
    dart_damage: float = 15.0
    """飞镖技能基础伤害值"""
    
    dart_count: int = 1
    """环绕玩家的飞镖数量"""
    
    dart_speed: float = 2.0
    """飞镖环绕飞行速度"""
    
    dart_radius: float = 80.0
    """飞镖环绕玩家的半径（像素）"""


@dataclass
class LevelConfig:
    """等级配置"""
    
    base_experience: int = 100
    """1级升2级所需的基础经验值"""
    
    experience_multiplier: float = 1.5
    """每级所需经验值的倍数（升级所需经验递增）"""
    
    hp_per_level: float = 20.0
    """每升一级增加的血量上限"""
    
    damage_per_level: float = 5.0
    """每升一级增加的基础攻击伤害"""
    
    levels_per_skill_upgrade: int = 1
    """每升多少级随机升级一个技能"""


@dataclass
class DifficultyConfig:
    """难度配置"""
    
    phase_duration: int = 1800
    """每个难度阶段持续的时间（帧数，1800帧=30秒）"""
    
    enemy_count_multiplier: float = 2
    """新阶段敌人数量的倍数（每阶段敌人数量增加）"""
    
    enemy_hp_multiplier: float = 2
    """新阶段敌人血量的倍数（每阶段敌人血量增加）"""
    
    enemy_damage_multiplier: float = 1.5
    """新阶段敌人伤害的倍数（每阶段敌人伤害增加）"""


@dataclass
class EnemyTypeConfig:
    """敌人类型配置"""
    
    warrior_hp: float = 80.0
    """战士敌人的最大血量"""
    
    warrior_damage: float = 10.0
    """战士敌人的近战伤害"""
    
    warrior_speed: float = 1.5
    """战士敌人的移动速度"""
    
    mage_hp: float = 60.0
    """法师敌人的最大血量"""
    
    mage_damage: float = 15.0
    """法师敌人的光球伤害"""
    
    mage_speed: float = 1.2
    """法师敌人的移动速度"""
    
    mage_projectile_speed: float = 5.0
    """法师敌人发射光球的飞行速度"""
    
    gunner_hp: float = 70.0
    """炮手敌人的最大血量"""
    
    gunner_damage: float = 20.0
    """炮手敌人的炮弹伤害"""
    
    gunner_speed: float = 1.0
    """炮手敌人的移动速度"""
    
    gunner_projectile_speed: float = 4.0
    """炮手敌人发射炮弹的飞行速度"""
    
    general_hp: float = 150.0
    """将军敌人的最大血量"""
    
    general_damage: float = 25.0
    """将军敌人的近战伤害"""
    
    general_speed: float = 1.8
    """将军敌人的移动速度"""
    
    general_attack_range: float = 100.0
    """将军敌人的近战攻击范围"""
    
    general_charge_damage: float = 40.0
    """将军敌人冲锋技能的伤害"""
    
    general_charge_distance: float = 150.0
    """将军敌人冲锋技能的冲锋距离"""
    
    general_charge_cooldown: int = 300
    """将军敌人冲锋技能的冷却时间（帧数，300帧=5秒）"""
    
    commander_hp: float = 250.0
    """统领敌人的最大血量"""
    
    commander_damage: float = 35.0
    """统领敌人的近战伤害"""
    
    commander_speed: float = 1.5
    """统领敌人的移动速度"""
    
    commander_attack_range: float = 120.0
    """统领敌人的近战攻击范围"""
    
    commander_shock_damage: float = 50.0
    """统领敌人震击技能的伤害"""
    
    commander_shock_radius: float = 150.0
    """统领敌人震击技能的作用范围半径"""
    
    commander_shock_cooldown: int = 360
    """统领敌人震击技能的冷却时间（帧数，360帧=6秒）"""


@dataclass
class PlayerConfig:
    """玩家配置"""
    
    max_hp: float = 100.0
    """玩家初始最大血量"""
    
    speed: float = 4.0
    """玩家移动速度（像素/帧）"""


@dataclass
class TeammateConfig:
    """AI队友配置"""
    
    max_hp: float = 100.0
    """AI队友初始最大血量"""
    
    speed: float = 2.5
    """AI队友移动速度（像素/帧）"""
    
    melee_damage: float = 15.0
    """AI队友近战攻击伤害"""
    
    ranged_damage: float = 10.0
    """AI队友远程攻击伤害"""
    
    melee_cooldown: int = 45
    """AI队友近战攻击冷却时间（帧数）"""
    
    ranged_cooldown: int = 60
    """AI队友远程攻击冷却时间（帧数）"""
    
    healing_potion_count: int = 3
    """AI队友初始携带的治疗药水数量"""
    
    detection_range: float = 200.0
    """AI队友检测敌人的范围半径（像素）"""
    
    melee_range: float = 80.0
    """AI队友近战攻击范围（像素）"""
    
    follow_distance: float = 100.0
    """AI队友跟随玩家的距离（像素）"""
    
    low_hp_threshold: float = 0.3
    """AI队友使用治疗药水的血量阈值（0-1之间，0.3表示血量低于30%时使用）"""
    
    behavior_priority: list = None
    """AI队友行为优先级列表，按顺序从高到低"""
    
    def __post_init__(self):
        if self.behavior_priority is None:
            self.behavior_priority = ['emergency', 'combat', 'follow', 'idle']


@dataclass
class SpawnConfig:
    """敌人生成配置"""
    
    max_enemies: int = 6
    """场上同时存在的最大敌人数量"""
    
    spawn_interval: int = 180
    """敌人生成间隔（帧数，180帧=3秒）"""
    
    min_spawn_x: float = 50.0
    """敌人生成区域的最小X坐标"""
    
    max_spawn_x: float = 700.0
    """敌人生成区域的最大X坐标"""
    
    min_spawn_y: float = 50.0
    """敌人生成区域的最小Y坐标"""
    
    max_spawn_y: float = 650.0
    """敌人生成区域的最大Y坐标"""


@dataclass
class HealthPackConfig:
    """血包配置"""
    
    heal_amount: float = 30.0
    """血包回复的血量值"""
    
    spawn_chance: float = 0.01
    """每帧血包生成的概率（0-1之间）"""
    
    max_packs: int = 3
    """场上同时存在的最大血包数量"""
    
    pickup_range: float = 40.0
    """血包拾取范围（像素）"""


@dataclass
class SkillPackConfig:
    """技能包配置"""
    
    spawn_chance: float = 0.005
    """每帧技能包生成的概率（0-1之间）"""
    
    max_packs: int = 2
    """场上同时存在的最大技能包数量"""
    
    pickup_range: float = 40.0
    """技能包拾取范围（像素）"""


@dataclass
class ScoreConfig:
    """分数配置"""
    
    warrior_score: int = 50
    """击杀战士敌人获得的基础分数"""
    
    warrior_exp: int = 20
    """击杀战士敌人获得的基础经验值"""
    
    mage_score: int = 80
    """击杀法师敌人获得的基础分数"""
    
    mage_exp: int = 30
    """击杀法师敌人获得的基础经验值"""
    
    gunner_score: int = 100
    """击杀炮手敌人获得的基础分数"""
    
    gunner_exp: int = 35
    """击杀炮手敌人获得的基础经验值"""
    
    general_score: int = 200
    """击杀将军敌人获得的基础分数"""
    
    general_exp: int = 60
    """击杀将军敌人获得的基础经验值"""
    
    commander_score: int = 400
    """击杀统领敌人获得的基础分数"""
    
    commander_exp: int = 100
    """击杀统领敌人获得的基础经验值"""
    
    time_multiplier: float = 1.1
    """每阶段分数和经验值的倍数"""
    
    max_score_history: int = 10
    """保存的历史最高分数记录数量"""


class GameConfig:
    """游戏总配置"""
    
    def __init__(self):
        """初始化游戏配置"""
        self.player = PlayerConfig()
        """玩家配置"""
        
        self.teammate = TeammateConfig()
        """AI队友配置"""
        
        self.skill = SkillConfig()
        """技能配置"""
        
        self.level = LevelConfig()
        """等级配置"""
        
        self.difficulty = DifficultyConfig()
        """难度配置"""
        
        self.enemy_type = EnemyTypeConfig()
        """敌人类型配置"""
        
        self.spawn = SpawnConfig()
        """敌人生成配置"""
        
        self.health_pack = HealthPackConfig()
        """血包配置"""
        
        self.skill_pack = SkillPackConfig()
        """技能包配置"""
        
        self.score = ScoreConfig()
        """分数配置"""
