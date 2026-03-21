import math
from typing import Optional
from .entities import Character, NPC, Enemy, Vector2
from .config import GameConfig


class CombatSystem:
    """近战战斗系统
    
    处理角色之间的近战攻击、伤害计算和攻击冷却
    """
    
    def __init__(self, config: GameConfig):
        """初始化战斗系统
        
        Args:
            config: 游戏配置
        """
        self.config = config
        self.melee_range = 50.0
    
    def can_attack(self, attacker: Character, target: Character) -> bool:
        """检查攻击者是否可以攻击目标
        
        Args:
            attacker: 攻击者
            target: 目标
            
        Returns:
            是否可以攻击
        """
        if not attacker.is_alive or not target.is_alive:
            return False
        
        distance = attacker.position.distance_to(target.position)
        if distance > self.melee_range:
            return False
        
        if hasattr(attacker, 'attack_cooldown_remaining'):
            if attacker.attack_cooldown_remaining > 0:
                return False
        
        return True
    
    def perform_attack(self, attacker: Character, target: Character) -> float:
        """执行攻击
        
        Args:
            attacker: 攻击者
            target: 目标
            
        Returns:
            造成的伤害值
        """
        if not self.can_attack(attacker, target):
            return 0.0
        
        damage = self._calculate_damage(attacker)
        target.take_damage(damage)
        self._apply_attack_cooldown(attacker)
        
        return damage
    
    def _calculate_damage(self, attacker: Character) -> float:
        """计算伤害值
        
        Args:
            attacker: 攻击者
            
        Returns:
            伤害值
        """
        if isinstance(attacker, NPC):
            return self.config.npc.melee_damage
        elif isinstance(attacker, Enemy):
            return self.config.enemy.damage
        else:
            return 10.0
    
    def _apply_attack_cooldown(self, attacker: Character) -> None:
        """应用攻击冷却
        
        Args:
            attacker: 攻击者
        """
        if hasattr(attacker, 'attack_cooldown_remaining'):
            if isinstance(attacker, NPC):
                attacker.attack_cooldown_remaining = self.config.npc.attack_cooldown
            elif isinstance(attacker, Enemy):
                attacker.attack_cooldown_remaining = self.config.enemy.attack_cooldown
            else:
                attacker.attack_cooldown_remaining = 60
    
    def update_cooldowns(self, character: Character) -> None:
        """更新角色的冷却时间
        
        Args:
            character: 角色
        """
        if hasattr(character, 'attack_cooldown_remaining'):
            if character.attack_cooldown_remaining > 0:
                character.attack_cooldown_remaining -= 1


def test_combat_system():
    """测试战斗系统"""
    config = GameConfig()
    combat = CombatSystem(config)
    
    print("=== 战斗系统测试 ===\n")
    
    npc = NPC("Warrior", Vector2(0, 0), config.npc.max_hp)
    enemy = Enemy("Goblin", Vector2(30, 0), config.enemy.max_hp)
    
    print(f"初始状态:")
    print(f"  {npc}")
    print(f"  {enemy}\n")
    
    print("1. 测试距离检测:")
    print(f"   NPC在距离30像素时能否攻击敌人: {combat.can_attack(npc, enemy)}")
    enemy.position = Vector2(60, 0)
    print(f"   NPC在距离60像素时能否攻击敌人: {combat.can_attack(npc, enemy)}")
    enemy.position = Vector2(30, 0)
    print()
    
    print("2. 测试NPC攻击敌人:")
    damage = combat.perform_attack(npc, enemy)
    print(f"   造成伤害: {damage:.0f}")
    print(f"   {enemy}")
    print(f"   攻击冷却剩余: {npc.attack_cooldown_remaining} 帧")
    print()
    
    print("3. 测试冷却机制:")
    can_attack_again = combat.can_attack(npc, enemy)
    print(f"   冷却期间能否再次攻击: {can_attack_again}")
    for _ in range(config.npc.attack_cooldown):
        combat.update_cooldowns(npc)
    can_attack_again = combat.can_attack(npc, enemy)
    print(f"   冷却结束后能否攻击: {can_attack_again}")
    print()
    
    print("4. 测试敌人攻击NPC:")
    damage = combat.perform_attack(enemy, npc)
    print(f"   造成伤害: {damage:.0f}")
    print(f"   {npc}")
    print()
    
    print("5. 测试连续攻击直至死亡:")
    attack_count = 0
    while enemy.is_alive:
        combat.update_cooldowns(npc)
        if combat.can_attack(npc, enemy):
            damage = combat.perform_attack(npc, enemy)
            attack_count += 1
            print(f"   攻击 {attack_count}: 造成 {damage:.0f} 伤害, 敌人剩余血量: {enemy.hp:.0f}")
    print(f"   敌人已死亡，共攻击 {attack_count} 次")
    print()
    
    print("6. 测试死亡状态下无法攻击:")
    damage = combat.perform_attack(enemy, npc)
    print(f"   死亡的敌人造成伤害: {damage:.0f}")
    print(f"   {npc}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_combat_system()
