import random
import math
from typing import List, Optional
from ai_teammate.entities import Vector2


class Skill:
    """技能基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.level = 1
        self.owner = None


class BulletSkill(Skill):
    """子弹技能"""
    
    def __init__(self, config):
        super().__init__("Bullet")
        self.config = config
        self.fire_rate = config.bullet_fire_rate
        self.bullet_count = config.bullet_count
        self.bullet_speed = config.bullet_speed
        self.damage = config.bullet_damage
        self.cooldown = 0
    
    def upgrade(self):
        """升级技能"""
        self.level += 1
        if random.random() < 0.5:
            self.fire_rate = max(10, self.fire_rate - 10)
        else:
            self.bullet_count += 1
        self.damage += self.config.bullet_damage * 0.2
    
    def update(self, owner, projectiles):
        """更新技能"""
        if self.cooldown > 0:
            self.cooldown -= 1
            return
        
        if self.cooldown <= 0:
            self.cooldown = self.fire_rate
            angle = owner.rotation
            for i in range(self.bullet_count):
                spread_angle = angle + (i - (self.bullet_count - 1) / 2) * 0.2
                direction = Vector2(math.cos(spread_angle), math.sin(spread_angle))
                start_pos = Vector2(
                    owner.position.x + direction.x * 30,
                    owner.position.y + direction.y * 30
                )
                from ai_teammate.game_items import Projectile
                from ai_teammate.entities import Player, Teammate
                projectile = Projectile(
                    start_pos,
                    direction * self.bullet_speed,
                    self.damage,
                    'friendly' if isinstance(owner, (Player, Teammate)) else 'enemy'
                )
                projectiles.append(projectile)


class DartSkill(Skill):
    """飞镖技能"""
    
    def __init__(self, config):
        super().__init__("Dart")
        self.config = config
        self.dart_count = config.dart_count
        self.dart_speed = config.dart_speed
        self.dart_radius = config.dart_radius
        self.damage = config.dart_damage
        self.darts = []
        self.angle = 0.0
    
    def upgrade(self):
        """升级技能"""
        self.level += 1
        choice = random.randint(0, 2)
        if choice == 0:
            self.dart_count += 1
        elif choice == 1:
            self.dart_speed += 0.5
        else:
            self.dart_radius += 20
        self.damage += self.config.dart_damage * 0.2
    
    def update(self, owner, darts):
        """更新技能"""
        self.angle += self.dart_speed * 0.02
        
        self.darts = []
        for i in range(self.dart_count):
            dart_angle = self.angle + (i * 2 * math.pi / self.dart_count)
            dart_pos = Vector2(
                owner.position.x + math.cos(dart_angle) * self.dart_radius,
                owner.position.y + math.sin(dart_angle) * self.dart_radius
            )
            self.darts.append((dart_pos, self.damage))
