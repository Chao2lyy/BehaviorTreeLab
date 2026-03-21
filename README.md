# BehaviorTreeLab (行为树实验室)

一个纯Python实现的行为树框架，参考了 BehaviorTree.CPP 和 fluid-behavior-tree 的架构设计。包含完整的AI队友行为树游戏应用！

## 项目名称
**BehaviorTreeLab** - 行为树实验室

## 功能特性

### 核心框架
- **Node (基类)**: 所有节点的抽象基类
- **Leaf (叶子节点)**:
  - `Action`: 执行具体动作
  - `Condition`: 检查条件
- **Composite (组合节点)**:
  - `Sequence`: 顺序执行，全部成功才成功
  - `Selector`: 选择执行，一个成功就成功
  - `Parallel`: 并行执行，支持多种策略
- **Decorator (装饰节点)**:
  - `Inverter`: 取反子节点状态
  - `Repeater`: 重复执行N次
  - `UntilFail`: 持续执行直到失败

### 数据共享
- **Blackboard**: 支持节点间数据共享，支持父子Blackboard继承关系

### AI队友行为树应用 - 基础版
完整的游戏AI队友行为系统，包含：
- 紧急治疗行为（血量<30%时使用治疗药水）
- 战斗行为（检测敌人、近战/远程攻击、面朝敌人）
- 跟随行为（与玩家距离>5时移动到玩家附近）
- 待机行为（默认Idle动画）
- ASCII可视化战斗场景模拟器

### AI队友行为树游戏 - 增强版
**完整的Pygame图形化游戏，包含：
- 🎮 图形化游戏界面（1100x700窗口）
- 🎯 敌人随机出生系统
- ❤️ 血包系统（可拾取回复血量
- 🏆 分数系统和历史排行榜
- ⚙️ 完整的参数配置系统
- 🤖 可配置的AI行为优先级
- 🎨 实时状态面板和操作说明

### AI队友行为树游戏 - 重构最终版 ⭐⭐
**完全重构的模块化架构版本，包含：
- 🎮 图形化游戏界面（1300x700窗口）
- 🧩 完全模块化的代码架构
- 🎯 多种敌人类型（战士、法师、枪手、将军、指挥官）
- 📈 难度递增系统（敌人频率、数量、强度随时间增加）
- 🎯 技能系统（子弹技能、飞镖技能）
- 📊 等级系统（经验值、技能升级）
- 💰 不同敌人不同奖励（分数和经验随时间递增）
- 🤝 经验值共享机制（玩家和AI队友经验完全共享）
- ❤️ 血包共享机制（任一角色拾取，两人同时加血）
- 🏆 分数系统和历史排行榜
- 🎨 实时状态面板和操作说明

![游戏演示](examples/ai_teammate_gui_refactored_final.gif)

## 安装

### 基础安装依赖
```bash
# 核心框架无需额外依赖，Python 3.6+ 即可
# 运行增强版游戏需要安装pygame
pip install pygame
```

## 快速开始

### 基础使用示例
```python
from behavior_tree import (
    NodeStatus,
    Blackboard,
    Action,
    Condition,
    Sequence,
    Selector,
    Inverter,
)

# 创建一个简单的行为树
tree = Sequence([
    Action(lambda: (print("起床"), NodeStatus.SUCCESS)[1]),
    Action(lambda: (print("刷牙"), NodeStatus.SUCCESS)[1]),
    Selector([
        Condition(lambda: False),
        Action(lambda: (print("吃早餐"), NodeStatus.SUCCESS)[1]),
    ]),
])

# 执行行为树
result = tree.tick()
print(f"结果: {result.value}")
```

## 运行示例

### 基础示例
```bash
python examples/simple_example.py
```

### AI队友基础行为树演示
```bash
python examples/test_ai_teammate.py      # 运行基础功能测试
python examples/ai_teammate_demo.py       # 运行交互式演示（选择场景）
```

### AI队友图形化游戏 - 基础版
```bash
python examples/ai_teammate_gui.py         # Pygame图形化界面
```

### AI队友图形化游戏 - 增强版 ⭐
```bash
python examples/ai_teammate_gui_enhanced.py  # 完整增强版（推荐）
```

### AI队友图形化游戏 - 重构最终版 ⭐⭐
```bash
python examples/ai_teammate_gui_refactored_final.py  # 重构最终版（模块化架构）
```

### 配置AI行为优先级示例
```bash
python examples/config_example.py           # 查看AI配置示例
```

## AI行为优先级配置

AI队友的行为优先级完全可配置！在 `ai_teammate/config.py` 中修改：

```python
# 可用的行为类型
# - 'emergency': 紧急治疗
# - 'combat': 战斗
# - 'follow': 跟随
# - 'idle': 待机

# 默认配置（战斗优先）
behavior_priority = ['emergency', 'combat', 'follow', 'idle']

# 保守型配置（跟随优先）
behavior_priority = ['emergency', 'follow', 'combat', 'idle']

# 好战型配置（只战斗不跟随）
behavior_priority = ['emergency', 'combat', 'idle']
```

更多配置示例请查看 `examples/config_example.py`

## 运行测试

```bash
python tests/test_behavior_tree.py -v
```

## 游戏操作说明

### 基础操作
- **WASD / 方向键**: 移动玩家
- **空格键**: 玩家攻击
- **Start Game**: 开始游戏
- **Pause/Resume**: 暂停/继续游戏
- **Restart**: 重新开始游戏

### 游戏玩法
1. 点击 "Start Game" 开始游戏
2. 控制玩家在地图上移动
3. AI队友会自动：
   - 检测并攻击敌人
   - 血量低时自动使用治疗药水
   - 拾取血包回复血量
   - 跟随玩家移动
4. 击杀敌人获得分数
5. 玩家死亡后游戏结束，分数自动保存
6. 查看历史排行榜！

## 项目结构

```
BehaviorTreeLab/
├── src/
│   └── behavior_tree/          # 核心行为树框架
│       ├── __init__.py
│       ├── types.py          # NodeStatus枚举
│       ├── blackboard.py     # Blackboard类
│       ├── node.py          # Node基类
│       ├── leaf.py          # Action和Condition节点
│       ├── composite.py     # Composite节点及其子类
│       └── decorator.py     # Decorator节点及其子类
├── examples/
│   ├── ai_teammate/          # AI队友行为树应用
│   │   ├── __init__.py
│   │   ├── entities.py       # 游戏实体类
│   │   ├── ai_behavior.py    # AI行为树实现
│   │   ├── config.py        # 游戏配置类
│   │   ├── score_manager.py # 分数管理器
│   │   ├── simulator.py     # 战斗场景模拟器
│   │   ├── skills.py        # 技能系统（重构新增）
│   │   ├── game_items.py    # 游戏物品（重构新增）
│   │   ├── level_system.py  # 等级系统（重构新增）
│   │   ├── advanced_enemies.py # 高级敌人（重构新增）
│   │   └── game_logic.py   # 核心游戏逻辑（重构新增）
│   ├── simple_example.py     # 基础使用示例
│   ├── test_ai_teammate.py  # AI队友功能测试
│   ├── ai_teammate_demo.py  # AI队友交互式演示
│   ├── ai_teammate_gui.py  # AI队友图形化游戏（基础版）
│   ├── ai_teammate_gui_enhanced.py  # AI队友图形化游戏（增强版）⭐
│   ├── ai_teammate_gui_refactored_final.py  # AI队友图形化游戏（重构最终版）⭐⭐
│   ├── config_example.py    # AI配置示例
│   └── scores.json        # 分数历史存档
├── tests/
│   └── test_behavior_tree.py # 核心框架单元测试
└── .trae/
    └── specs/              # 规划文档
```

## 许可证

本项目采用 **MIT License** 许可证。

```
MIT License

Copyright (c) 2026 BehaviorTreeLab

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

完整许可证文本请查看项目根目录下的 [LICENSE](LICENSE) 文件。

## 未来计划
- [ ] 添加更多行为树节点类型
- [ ] 添加行为树可视化编辑器
- [ ] 支持行为树导入/导出功能
- [ ] 添加更多AI行为示例
- [ ] 性能优化
- [ ] 文档完善
