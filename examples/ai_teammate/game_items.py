from ai_teammate.entities import Vector2


class Projectile:
    """投射物类"""
    
    def __init__(self, position: Vector2, velocity: Vector2, damage: float, team: str):
        self.position = position
        self.velocity = velocity
        self.damage = damage
        self.team = team
        self.alive = True
        self.radius = 8


class Dart:
    """飞镖类"""
    
    def __init__(self, position: Vector2, damage: float):
        self.position = position
        self.damage = damage
        self.radius = 12


class HealthPack:
    """血包类"""
    
    def __init__(self, position: Vector2, heal_amount: float):
        self.position = position
        self.heal_amount = heal_amount
        self.radius = 15


class SkillPack:
    """技能包类"""
    
    def __init__(self, position: Vector2, skill_type: str):
        self.position = position
        self.skill_type = skill_type
        self.radius = 20
