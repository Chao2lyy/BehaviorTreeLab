import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

print("Testing modules...")

try:
    from ai_teammate.skills import Skill, BulletSkill, DartSkill
    print("✓ skills.py imported successfully")
except Exception as e:
    print(f"✗ Error importing skills.py: {e}")

try:
    from ai_teammate.game_items import Projectile, Dart, HealthPack, SkillPack
    print("✓ game_items.py imported successfully")
except Exception as e:
    print(f"✗ Error importing game_items.py: {e}")

try:
    from ai_teammate.level_system import LevelSystem
    print("✓ level_system.py imported successfully")
except Exception as e:
    print(f"✗ Error importing level_system.py: {e}")

try:
    from ai_teammate.advanced_enemies import EnemyType, AdvancedEnemy
    print("✓ advanced_enemies.py imported successfully")
except Exception as e:
    print(f"✗ Error importing advanced_enemies.py: {e}")

try:
    from ai_teammate.game_logic import GameLogic
    print("✓ game_logic.py imported successfully")
except Exception as e:
    print(f"✗ Error importing game_logic.py: {e}")

try:
    from ai_teammate.config import GameConfig
    from ai_teammate.score_manager import ScoreManager
    config = GameConfig()
    score_manager = ScoreManager(config)
    logic = GameLogic(config, score_manager, 750, 700)
    print("✓ GameLogic initialized successfully")
except Exception as e:
    print(f"✗ Error initializing GameLogic: {e}")
    import traceback
    traceback.print_exc()

print("\nAll tests completed!")
