"""
AI行为优先级配置示例
====================

这个文件展示了如何配置AI队友的行为优先级。

可用的行为类型:
- 'emergency': 紧急治疗（血量低时使用治疗药水）
- 'combat': 战斗（寻找并攻击敌人）
- 'follow': 跟随玩家
- 'idle': 待机

配置说明:
- 行为按列表顺序执行优先级，前面的行为优先级更高
- 可以通过修改 behavior_priority 列表来调整优先级
"""

from ai_teammate.config import GameConfig, TeammateConfig

# 示例1: 默认配置（战斗优先）
print("示例1: 默认配置（战斗优先）")
config1 = GameConfig()
print(f"  行为优先级: {config1.teammate.behavior_priority}")
print(f"  说明: 紧急治疗 > 战斗 > 跟随 > 待机")
print()

# 示例2: 保守型AI（跟随优先，只在必要时战斗）
print("示例2: 保守型AI（跟随优先）")
config2 = GameConfig()
config2.teammate.behavior_priority = ['emergency', 'follow', 'combat', 'idle']
print(f"  行为优先级: {config2.teammate.behavior_priority}")
print(f"  说明: 紧急治疗 > 跟随 > 战斗 > 待机")
print()

# 示例3: 好战型AI（战斗优先，不跟随）
print("示例3: 好战型AI（战斗优先，不跟随）")
config3 = GameConfig()
config3.teammate.behavior_priority = ['emergency', 'combat', 'idle']
print(f"  行为优先级: {config3.teammate.behavior_priority}")
print(f"  说明: 紧急治疗 > 战斗 > 待机（不跟随玩家）")
print()

# 示例4: 纯辅助AI（只跟随和治疗，不战斗）
print("示例4: 纯辅助AI（只跟随和治疗，不战斗）")
config4 = GameConfig()
config4.teammate.behavior_priority = ['emergency', 'follow', 'idle']
print(f"  行为优先级: {config4.teammate.behavior_priority}")
print(f"  说明: 紧急治疗 > 跟随 > 待机（不战斗）")
print()

# 示例5: 调整其他参数
print("示例5: 调整其他AI参数")
config5 = GameConfig()
config5.teammate.low_hp_threshold = 0.5  # 血量低于50%就治疗
config5.teammate.detection_range = 300.0  # 更远的检测范围
config5.teammate.speed = 3.0  # 更快的移动速度
config5.teammate.melee_damage = 25.0  # 更高的近战伤害
print(f"  低血量阈值: {config5.teammate.low_hp_threshold}")
print(f"  检测范围: {config5.teammate.detection_range}")
print(f"  移动速度: {config5.teammate.speed}")
print(f"  近战伤害: {config5.teammate.melee_damage}")
print()

print("如何在游戏中使用自定义配置:")
print("  1. 修改 ai_teammate/config.py 中的 TeammateConfig 类")
print("  2. 或者在 ai_teammate_gui_enhanced.py 的 init_game() 方法中")
print("     添加自定义配置代码")
print()
print("例如:")
print("  # 在 init_game() 中")
print("  self.config = GameConfig()")
print("  self.config.teammate.behavior_priority = ['emergency', 'combat', 'follow', 'idle']")
print("  self.config.teammate.speed = 3.0")
