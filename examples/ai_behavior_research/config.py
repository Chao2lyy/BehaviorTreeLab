"""游戏配置类"""

from dataclasses import dataclass


@dataclass
class NPCConfig:
    """NPC配置"""
    
    max_hp: float = 100.0
    """NPC最大血量"""
    
    speed: float = 2.5
    """NPC移动速度（像素/帧）"""
    
    melee_damage: float = 15.0
    """NPC近战伤害"""
    
    attack_range: float = 80.0
    """NPC攻击范围（像素）"""
    
    attack_cooldown: int = 45
    """NPC攻击冷却时间（帧数）"""
    
    detection_range: float = 200.0
    """NPC检测敌人的范围半径（像素）"""
    
    follow_distance: float = 100.0
    """NPC跟随玩家的距离（像素）"""
    
    guard_range: float = 150.0
    """NPC守卫的范围半径（像素）"""
    
    low_hp_threshold: float = 0.3
    """NPC逃跑的血量阈值（0-1之间）"""
    
    heal_amount: float = 30.0
    """NPC治疗的血量值"""
    
    heal_cooldown: int = 300
    """NPC治疗冷却时间（帧数）"""


@dataclass
class EnemyConfig:
    """敌人配置"""
    
    max_hp: float = 80.0
    """敌人最大血量"""
    
    speed: float = 1.5
    """敌人移动速度（像素/帧）"""
    
    damage: float = 10.0
    """敌人伤害"""
    
    attack_range: float = 60.0
    """敌人攻击范围（像素）"""
    
    attack_cooldown: int = 60
    """敌人攻击冷却时间（帧数）"""
    
    detection_range: float = 250.0
    """敌人检测目标的范围半径（像素）"""


@dataclass
class MapConfig:
    """地图配置"""
    
    grid_size: float = 32.0
    """网格大小（像素）"""
    
    map_width: float = 800.0
    """地图宽度（像素）"""
    
    map_height: float = 600.0
    """地图高度（像素）"""
    
    spawn_zone_min_x: float = 50.0
    """敌人生成区域最小X坐标"""
    
    spawn_zone_max_x: float = 750.0
    """敌人生成区域最大X坐标"""
    
    spawn_zone_min_y: float = 50.0
    """敌人生成区域最小Y坐标"""
    
    spawn_zone_max_y: float = 550.0
    """敌人生成区域最大Y坐标"""


@dataclass
class UtilityWeights:
    """Utility AI评分权重配置 - 更加平衡的策略
    
    Utility AI特点：
    - 平衡考虑所有因素
    - 根据评分最高行为
    - 平滑的行为过渡
    """
    
    attack_enemy_threat_weight: float = 0.4
    """攻击评分中敌人威胁的权重"""
    
    attack_my_health_weight: float = 0.4
    """攻击评分中自身血量的权重"""
    
    attack_ammo_level_weight: float = 0.2
    """攻击评分中弹药量的权重"""
    
    heal_my_health_weight: float = 0.6
    """治疗评分中自身血量的权重"""
    
    heal_safe_area_weight: float = 0.4
    """治疗评分中安全区域的权重"""
    
    flee_my_health_weight: float = 0.4
    """逃跑评分中自身血量的权重"""
    
    flee_enemy_count_weight: float = 0.3
    """逃跑评分中敌人数量的权重"""
    
    flee_enemy_threat_weight: float = 0.3
    """逃跑评分中敌人威胁的权重"""
    
    guard_proximity_weight: float = 1.2
    """守卫评分中靠近警戒点的权重"""


class GameConfig:
    """游戏总配置"""
    
    def __init__(self):
        """初始化游戏配置"""
        self.npc = NPCConfig()
        """NPC配置"""
        
        self.enemy = EnemyConfig()
        """敌人配置"""
        
        self.map = MapConfig()
        """地图配置"""
        
        self.utility_weights = UtilityWeights()
        """Utility AI评分权重配置"""
