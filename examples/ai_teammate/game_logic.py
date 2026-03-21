import random
from typing import List, Optional
from behavior_tree import Blackboard
from ai_teammate.entities import Player, Teammate, Enemy, Vector2
from ai_teammate.ai_behavior import AITeammate
from ai_teammate.config import GameConfig
from ai_teammate.score_manager import ScoreManager
from ai_teammate.skills import Skill, BulletSkill, DartSkill
from ai_teammate.game_items import Projectile, HealthPack, SkillPack
from ai_teammate.level_system import LevelSystem
from ai_teammate.advanced_enemies import EnemyType, AdvancedEnemy


class GameLogic:
    """核心游戏逻辑"""
    
    def __init__(self, config: GameConfig, score_manager: ScoreManager, game_area_width: int, game_area_height: int):
        self.config = config
        self.score_manager = score_manager
        self.game_area_width = game_area_width
        self.game_area_height = game_area_height
        
        self.blackboard = Blackboard()
        self.game_over = False
        self.game_started = False
        self.game_time = 0
        self.difficulty_phase = 1
        self.enemy_spawn_timer = 0
        
        self.player = Player(Vector2(game_area_width / 2 - 75, game_area_height / 2))
        self.player.max_hp = config.player.max_hp
        self.player.hp = config.player.max_hp
        
        self.teammate = Teammate("AI Teammate", Vector2(game_area_width / 2 + 75, game_area_height / 2))
        self.teammate.max_hp = config.teammate.max_hp
        self.teammate.hp = config.teammate.max_hp
        self.teammate.healing_potion_count = config.teammate.healing_potion_count
        
        self.player_speed = config.player.speed
        
        self.enemies: List[AdvancedEnemy] = []
        self.health_packs: List[HealthPack] = []
        self.skill_packs: List[SkillPack] = []
        self.projectiles: List[Projectile] = []
        
        self.player_level = LevelSystem(config.level)
        self.teammate_level = LevelSystem(config.level)
        
        self.player_skills = {'bullet': BulletSkill(config.skill)}
        self.teammate_skills = {'bullet': BulletSkill(config.skill)}
        self.all_skills_learned = False
        
        self.player_speed = config.player.speed
        
        self.ai_teammate = AITeammate(self.teammate, self.player, self.blackboard, config.teammate)
    
    def reset(self):
        """重置游戏状态"""
        self.__init__(self.config, self.score_manager, self.game_area_width, self.game_area_height)
    
    def start_game(self):
        """开始游戏"""
        self.game_started = True
    
    def restart_game(self):
        """重新开始游戏"""
        self.game_started = False
        self.reset()
    
    def update(self):
        """更新游戏状态"""
        if self.game_over or not self.game_started:
            return
        
        self.game_time += 1
        
        new_phase = (self.game_time // self.config.difficulty.phase_duration) + 1
        if new_phase > self.difficulty_phase:
            self.difficulty_phase = new_phase
        
        self.update_skills()
        self.update_projectiles()
        self.update_darts()
        self.update_enemies()
        self.spawn_enemies()
        self.spawn_health_packs()
        self.spawn_skill_packs()
        self.check_health_pack_pickup()
        self.check_skill_pack_pickup()
        
        if self.teammate.is_alive:
            self.ai_teammate.update()
            self.check_ai_kills()
        
        self.check_game_over()
    
    def update_darts(self):
        """更新飞镖伤害"""
        for dart_pos, dart_damage in getattr(self.player_skills.get('dart'), 'darts', []):
            for enemy in self.enemies:
                if enemy.is_alive:
                    dist = dart_pos.distance_to(enemy.position)
                    if dist < 35:
                        enemy.take_damage(dart_damage + self.player_level.level * self.config.level.damage_per_level)
                        if not enemy.is_alive and not enemy.counted_for_score:
                            enemy.counted_for_score = True
                            score, exp = self.get_enemy_rewards(enemy.enemy_type)
                            self.score_manager.add_score(score)
                            self.player_level.add_experience(exp)
                            self.teammate_level.add_experience(exp)
                            self.check_level_up()
        
        for dart_pos, dart_damage in getattr(self.teammate_skills.get('dart'), 'darts', []):
            for enemy in self.enemies:
                if enemy.is_alive:
                    dist = dart_pos.distance_to(enemy.position)
                    if dist < 35:
                        enemy.take_damage(dart_damage + self.teammate_level.level * self.config.level.damage_per_level)
                        if not enemy.is_alive and not enemy.counted_for_score:
                            enemy.counted_for_score = True
                            score, exp = self.get_enemy_rewards(enemy.enemy_type)
                            self.score_manager.add_score(score)
                            self.player_level.add_experience(exp)
                            self.teammate_level.add_experience(exp)
                            self.check_level_up()
    
    def update_skills(self):
        """更新技能"""
        if self.player.is_alive:
            if 'bullet' in self.player_skills:
                self.player_skills['bullet'].update(self.player, self.projectiles)
            if 'dart' in self.player_skills:
                self.player_skills['dart'].update(self.player, [])
        
        if self.teammate.is_alive:
            if 'bullet' in self.teammate_skills:
                self.teammate_skills['bullet'].update(self.teammate, self.projectiles)
            if 'dart' in self.teammate_skills:
                self.teammate_skills['dart'].update(self.teammate, [])
    
    def update_projectiles(self):
        """更新投射物"""
        for proj in self.projectiles[:]:
            proj.position = proj.position + proj.velocity
            
            if (proj.position.x < 0 or proj.position.x > self.game_area_width or
                proj.position.y < 0 or proj.position.y > self.game_area_height):
                proj.alive = False
                continue
            
            if proj.team == 'friendly':
                for enemy in self.enemies:
                    if enemy.is_alive:
                        dist = proj.position.distance_to(enemy.position)
                        if dist < 35:
                            enemy.take_damage(proj.damage + self.player_level.level * self.config.level.damage_per_level)
                            proj.alive = False
                            if not enemy.is_alive and not enemy.counted_for_score:
                                enemy.counted_for_score = True
                                score, exp = self.get_enemy_rewards(enemy.enemy_type)
                                self.score_manager.add_score(score)
                                self.player_level.add_experience(exp)
                                self.teammate_level.add_experience(exp)
                                self.check_level_up()
                            break
            else:
                for target in [self.player, self.teammate]:
                    if target.is_alive:
                        dist = proj.position.distance_to(target.position)
                        if dist < 35:
                            target.take_damage(proj.damage)
                            proj.alive = False
                            break
        
        self.projectiles = [p for p in self.projectiles if p.alive]
    
    def get_enemy_rewards(self, enemy_type: str) -> tuple:
        """获取敌人的分数和经验值"""
        rewards_map = {
            EnemyType.WARRIOR: (self.config.score.warrior_score, self.config.score.warrior_exp),
            EnemyType.MAGE: (self.config.score.mage_score, self.config.score.mage_exp),
            EnemyType.GUNNER: (self.config.score.gunner_score, self.config.score.gunner_exp),
            EnemyType.GENERAL: (self.config.score.general_score, self.config.score.general_exp),
            EnemyType.COMMANDER: (self.config.score.commander_score, self.config.score.commander_exp)
        }
        
        base_score, base_exp = rewards_map.get(enemy_type, (50, 20))
        time_mult = (self.config.score.time_multiplier) ** (self.difficulty_phase - 1)
        final_score = int(base_score * time_mult)
        final_exp = int(base_exp * time_mult)
        
        return (final_score, final_exp)
    
    def check_level_up(self):
        """检查升级"""
        if self.player_level.level > 1 and (self.player_level.level - 1) % self.config.level.levels_per_skill_upgrade == 0:
            self.upgrade_random_skill(self.player_skills)
            self.upgrade_random_skill(self.teammate_skills)
        
        hp_bonus = (self.player_level.level - 1) * self.config.level.hp_per_level
        self.player.max_hp = self.config.player.max_hp + hp_bonus
        self.teammate.max_hp = self.config.teammate.max_hp + hp_bonus
    
    def upgrade_random_skill(self, skills):
        """随机升级技能"""
        if skills:
            skill_name = random.choice(list(skills.keys()))
            skills[skill_name].upgrade()
    
    def update_enemies(self):
        """更新敌人AI"""
        for enemy in self.enemies:
            if not enemy.is_alive:
                continue
            
            if enemy.attack_cooldown > 0:
                enemy.attack_cooldown -= 1
            
            if enemy.enemy_type in [EnemyType.GENERAL, EnemyType.COMMANDER]:
                if enemy.charge_cooldown > 0:
                    enemy.charge_cooldown -= 1
                if enemy.shock_cooldown > 0:
                    enemy.shock_cooldown -= 1
            
            targets = []
            if self.player.is_alive:
                targets.append((self.player, self.player.position.distance_to(enemy.position)))
            if self.teammate.is_alive:
                targets.append((self.teammate, self.teammate.position.distance_to(enemy.position)))
            
            if not targets:
                continue
            
            targets.sort(key=lambda x: x[1])
            target, dist = targets[0]
            
            if enemy.enemy_type in [EnemyType.WARRIOR, EnemyType.GENERAL, EnemyType.COMMANDER]:
                if dist < enemy.attack_range:
                    if enemy.attack_cooldown <= 0:
                        target.take_damage(enemy.damage)
                        enemy.attack_cooldown = enemy.attack_cooldown_max
                        enemy.look_at(target.position)
                else:
                    direction = target.position - enemy.position
                    direction = direction.normalized()
                    new_x = enemy.position.x + direction.x * enemy.speed
                    new_y = enemy.position.y + direction.y * enemy.speed
                    new_x = max(30, min(self.game_area_width - 30, new_x))
                    new_y = max(30, min(self.game_area_height - 30, new_y))
                    enemy.position = Vector2(new_x, new_y)
                    enemy.look_at(target.position)
            elif enemy.enemy_type in [EnemyType.MAGE, EnemyType.GUNNER]:
                if dist < enemy.attack_range:
                    if enemy.attack_cooldown <= 0:
                        enemy.look_at(target.position)
                        direction = target.position - enemy.position
                        direction = direction.normalized()
                        start_pos = Vector2(
                            enemy.position.x + direction.x * 30,
                            enemy.position.y + direction.y * 30
                        )
                        projectile = Projectile(
                            start_pos,
                            direction * enemy.projectile_speed,
                            enemy.damage,
                            'enemy'
                        )
                        self.projectiles.append(projectile)
                        enemy.attack_cooldown = enemy.attack_cooldown_max
                else:
                    direction = target.position - enemy.position
                    direction = direction.normalized()
                    new_x = enemy.position.x + direction.x * enemy.speed
                    new_y = enemy.position.y + direction.y * enemy.speed
                    new_x = max(30, min(self.game_area_width - 30, new_x))
                    new_y = max(30, min(self.game_area_height - 30, new_y))
                    enemy.position = Vector2(new_x, new_y)
                    enemy.look_at(target.position)
            
            if enemy.enemy_type == EnemyType.GENERAL:
                if enemy.charge_cooldown <= 0 and dist < 200:
                    enemy.is_charging = True
                    enemy.charge_start = Vector2(enemy.position.x, enemy.position.y)
                    enemy.charge_target = Vector2(target.position.x, target.position.y)
                    enemy.charge_cooldown = enemy.charge_cooldown_max
            
            if enemy.is_charging and enemy.charge_start and enemy.charge_target:
                direction = enemy.charge_target - enemy.charge_start
                dist_total = direction.distance_to(Vector2(0, 0))
                if dist_total > 0:
                    direction = direction.normalized()
                    new_x = enemy.position.x + direction.x * 8
                    new_y = enemy.position.y + direction.y * 8
                    enemy.position = Vector2(new_x, new_y)
                    
                    for t in [self.player, self.teammate]:
                        if t.is_alive:
                            d = enemy.position.distance_to(t.position)
                            if d < 40:
                                t.take_damage(enemy.charge_damage)
                    
                    if enemy.position.distance_to(enemy.charge_start) > enemy.charge_distance:
                        enemy.is_charging = False
                        enemy.charge_start = None
                        enemy.charge_target = None
            
            if enemy.enemy_type == EnemyType.COMMANDER:
                if enemy.shock_cooldown <= 0:
                    for t in [self.player, self.teammate]:
                        if t.is_alive:
                            d = enemy.position.distance_to(t.position)
                            if d < enemy.shock_radius:
                                t.take_damage(enemy.shock_damage)
                    enemy.shock_cooldown = enemy.shock_cooldown_max
        
        self.enemies = [e for e in self.enemies if e.is_alive]
    
    def spawn_enemies(self):
        """敌人生成"""
        self.enemy_spawn_timer += 1
        
        difficulty_mult = (self.config.difficulty.enemy_hp_multiplier) ** (self.difficulty_phase - 1)
        max_enemies = int(self.config.spawn.max_enemies * (self.config.difficulty.enemy_count_multiplier) ** (self.difficulty_phase - 1))
        spawn_interval = max(30, self.config.spawn.spawn_interval - self.difficulty_phase * 25)
        enemies_per_spawn = min(3, 1 + (self.difficulty_phase - 1) // 2)
        
        if len(self.enemies) < max_enemies:
            if self.enemy_spawn_timer >= spawn_interval:
                self.enemy_spawn_timer = 0
                
                base_x = random.uniform(self.config.spawn.min_spawn_x, self.config.spawn.max_spawn_x)
                base_y = random.uniform(self.config.spawn.min_spawn_y, self.config.spawn.max_spawn_y)
                
                types = [EnemyType.WARRIOR]
                weights = [1.0]
                
                if self.difficulty_phase >= 2:
                    types.append(EnemyType.MAGE)
                    mage_weight = min(0.8, 0.2 + self.difficulty_phase * 0.1)
                    weights.append(mage_weight)
                
                if self.difficulty_phase >= 3:
                    types.append(EnemyType.GUNNER)
                    gunner_weight = min(0.6, 0.1 + self.difficulty_phase * 0.08)
                    weights.append(gunner_weight)
                
                if self.difficulty_phase >= 4:
                    types.append(EnemyType.GENERAL)
                    general_weight = min(0.4, 0.05 + self.difficulty_phase * 0.05)
                    weights.append(general_weight)
                
                if self.difficulty_phase >= 6:
                    types.append(EnemyType.COMMANDER)
                    commander_weight = min(0.25, 0.03 + self.difficulty_phase * 0.03)
                    weights.append(commander_weight)
                
                for i in range(enemies_per_spawn):
                    if len(self.enemies) >= max_enemies:
                        break
                    
                    offset_x = random.uniform(-30, 30) if i > 0 else 0
                    offset_y = random.uniform(-30, 30) if i > 0 else 0
                    
                    x = base_x + offset_x
                    y = base_y + offset_y
                    
                    x = max(self.config.spawn.min_spawn_x, min(self.config.spawn.max_spawn_x, x))
                    y = max(self.config.spawn.min_spawn_y, min(self.config.spawn.max_spawn_y, y))
                    
                    enemy_type = random.choices(types, weights=weights, k=1)[0]
                    enemy_name = f"{enemy_type.capitalize()} {len(self.enemies) + 1}"
                    
                    enemy = AdvancedEnemy(enemy_name, Vector2(x, y), enemy_type, self.config.enemy_type, difficulty_mult)
                    enemy.counted_for_score = False
                    self.enemies.append(enemy)
                    self.ai_teammate.add_enemy(enemy)
    
    def spawn_health_packs(self):
        """血包生成"""
        if len(self.health_packs) < self.config.health_pack.max_packs:
            if random.random() < self.config.health_pack.spawn_chance:
                x = random.uniform(50, self.game_area_width - 50)
                y = random.uniform(50, self.game_area_height - 50)
                self.health_packs.append(HealthPack(Vector2(x, y), self.config.health_pack.heal_amount))
    
    def spawn_skill_packs(self):
        """技能包生成"""
        if self.all_skills_learned:
            return
        
        available_skills = []
        if 'dart' not in self.player_skills:
            available_skills.append('dart')
        
        if len(available_skills) > 0 and len(self.skill_packs) < self.config.skill_pack.max_packs:
            if random.random() < self.config.skill_pack.spawn_chance:
                x = random.uniform(50, self.game_area_width - 50)
                y = random.uniform(50, self.game_area_height - 50)
                skill_type = random.choice(available_skills)
                self.skill_packs.append(SkillPack(Vector2(x, y), skill_type))
    
    def check_health_pack_pickup(self):
        """检查血包拾取"""
        packs_to_remove = []
        
        for pack in self.health_packs:
            if self.player.is_alive:
                dist = self.player.position.distance_to(pack.position)
                if dist < self.config.health_pack.pickup_range:
                    self.player.heal(pack.heal_amount)
                    if self.teammate.is_alive:
                        self.teammate.heal(pack.heal_amount)
                    packs_to_remove.append(pack)
                    continue
            
            if self.teammate.is_alive:
                dist = self.teammate.position.distance_to(pack.position)
                if dist < self.config.health_pack.pickup_range:
                    self.teammate.heal(pack.heal_amount)
                    if self.player.is_alive:
                        self.player.heal(pack.heal_amount)
                    packs_to_remove.append(pack)
        
        for pack in packs_to_remove:
            if pack in self.health_packs:
                self.health_packs.remove(pack)
    
    def check_skill_pack_pickup(self):
        """检查技能包拾取"""
        packs_to_remove = []
        
        for pack in self.skill_packs:
            if self.player.is_alive:
                dist = self.player.position.distance_to(pack.position)
                if dist < self.config.skill_pack.pickup_range:
                    if pack.skill_type == 'dart' and 'dart' not in self.player_skills:
                        self.player_skills['dart'] = DartSkill(self.config.skill)
                        self.teammate_skills['dart'] = DartSkill(self.config.skill)
                    packs_to_remove.append(pack)
                    
                    if len(self.player_skills) >= 2:
                        self.all_skills_learned = True
        
        for pack in packs_to_remove:
            if pack in self.skill_packs:
                self.skill_packs.remove(pack)
    
    def check_ai_kills(self):
        """检查AI击杀的敌人"""
        pass
    
    def check_game_over(self):
        """检查游戏是否结束"""
        if not self.player.is_alive and not self.game_over:
            self.game_over = True
            self.score_manager.save_score()
