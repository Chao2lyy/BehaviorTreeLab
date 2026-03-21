from ai_teammate.entities import Character, Vector2


class EnemyType:
    """敌人类型枚举"""
    WARRIOR = "warrior"
    MAGE = "mage"
    GUNNER = "gunner"
    GENERAL = "general"
    COMMANDER = "commander"


class AdvancedEnemy(Character):
    """高级敌人类"""
    
    def __init__(self, name: str, position: Vector2, enemy_type: str, config, difficulty_multiplier: float = 1.0):
        max_hp = 0
        self.enemy_type = enemy_type
        
        # 初始化所有敌人的通用属性
        self.is_charging = False
        self.charge_target = None
        self.charge_start = None
        self.charge_cooldown = 0
        self.shock_cooldown = 0
        
        if enemy_type == EnemyType.WARRIOR:
            max_hp = config.warrior_hp * difficulty_multiplier
            self.damage = config.warrior_damage * difficulty_multiplier
            self.speed = config.warrior_speed
            self.attack_range = 60.0
            self.attack_cooldown_max = 60
        elif enemy_type == EnemyType.MAGE:
            max_hp = config.mage_hp * difficulty_multiplier
            self.damage = config.mage_damage * difficulty_multiplier
            self.speed = config.mage_speed
            self.attack_range = 200.0
            self.attack_cooldown_max = 90
            self.projectile_speed = config.mage_projectile_speed
        elif enemy_type == EnemyType.GUNNER:
            max_hp = config.gunner_hp * difficulty_multiplier
            self.damage = config.gunner_damage * difficulty_multiplier
            self.speed = config.gunner_speed
            self.attack_range = 250.0
            self.attack_cooldown_max = 120
            self.projectile_speed = config.gunner_projectile_speed
        elif enemy_type == EnemyType.GENERAL:
            max_hp = config.general_hp * difficulty_multiplier
            self.damage = config.general_damage * difficulty_multiplier
            self.speed = config.general_speed
            self.attack_range = config.general_attack_range
            self.attack_cooldown_max = 45
            self.charge_damage = config.general_charge_damage * difficulty_multiplier
            self.charge_distance = config.general_charge_distance
            self.charge_cooldown_max = config.general_charge_cooldown
        elif enemy_type == EnemyType.COMMANDER:
            max_hp = config.commander_hp * difficulty_multiplier
            self.damage = config.commander_damage * difficulty_multiplier
            self.speed = config.commander_speed
            self.attack_range = config.commander_attack_range
            self.attack_cooldown_max = 40
            self.charge_damage = config.general_charge_damage * difficulty_multiplier
            self.charge_distance = config.general_charge_distance
            self.charge_cooldown_max = config.general_charge_cooldown
            self.shock_damage = config.commander_shock_damage * difficulty_multiplier
            self.shock_radius = config.commander_shock_radius
            self.shock_cooldown_max = config.commander_shock_cooldown
        
        super().__init__(name, position, max_hp)
        self.attack_cooldown = 0
        self.counted_for_score = False
