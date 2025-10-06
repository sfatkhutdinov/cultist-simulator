#!/usr/bin/env python3
"""
Training Readiness Verification Script

Checks all prerequisites before starting a training run:
- Game window detection
- Screen capture permissions
- Module imports
- Database connectivity
- Directory structure

Run this before your first training session!
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_imports():
    """Verify all required modules can be imported."""
    print("\n🔍 Checking module imports...")
    
    try:
        import src.vision
        print("  ✓ Vision module")
    except ImportError as e:
        print(f"  ✗ Vision module: {e}")
        return False
    
    try:
        import src.learning
        print("  ✓ Learning module")
    except ImportError as e:
        print(f"  ✗ Learning module: {e}")
        return False
    
    try:
        import src.automation
        print("  ✓ Automation module")
    except ImportError as e:
        print(f"  ✗ Automation module: {e}")
        return False
    
    try:
        import src.safety
        print("  ✓ Safety module")
    except ImportError as e:
        print(f"  ✗ Safety module: {e}")
        return False
    
    try:
        import src.nlp
        print("  ✓ NLP module")
    except ImportError as e:
        print(f"  ✗ NLP module: {e}")
        return False
    
    return True


def check_game_window():
    """Check if Cultist Simulator window is running and detectable."""
    print("\n🎮 Checking game window...")
    
    try:
        from src.automation.window_manager import get_active_window_bounds
        
        window = get_active_window_bounds("Cultist Simulator")
        
        if window:
            print(f"  ✓ Window found: Cultist Simulator")
            print(f"    Location: ({window.x}, {window.y})")
            print(f"    Size: {window.width}×{window.height}")
            return True
        else:
            print("  ✗ Window not found or not active")
            print("    Make sure Cultist Simulator is running and active!")
            return False
            
    except Exception as e:
        print(f"  ✗ Error detecting window: {e}")
        return False


def check_screen_capture():
    """Test screen capture capability."""
    print("\n📸 Checking screen capture...")
    
    try:
        from src.vision.screen_capture import capture_window_screenshot
        from src.automation.window_manager import get_active_window_bounds
        
        window = get_active_window_bounds("Cultist Simulator")
        
        if not window:
            print("  ⚠️  Skipped (window not found or not active)")
            return False
        
        image, bounds = capture_window_screenshot("Cultist Simulator")
        
        if image is not None and image.size > 0:
            print(f"  ✓ Screen capture working")
            print(f"    Image shape: {image.shape}")
            print(f"    Bounds: {bounds}")
            return True
        else:
            print("  ✗ Screen capture failed")
            print("    Grant Screen Recording permission:")
            print("    System Settings → Privacy & Security → Screen Recording")
            print("    Enable for Terminal/Python, then restart terminal")
            return False
            
    except Exception as e:
        print(f"  ✗ Screen capture error: {e}")
        print("    This usually means missing Screen Recording permission")
        return False


def check_database():
    """Verify database connectivity."""
    print("\n🗄️  Checking database...")
    
    try:
        from src.learning.knowledge_base import KnowledgeBase
        
        kb = KnowledgeBase()
        
        # Test query
        if kb.conn:
            cursor = kb.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            kb.close()
            
            print(f"  ✓ Database connected")
            print(f"    Path: data/knowledge_base.db")
            print(f"    Tables: {len(tables)}")
            return True
        else:
            print(f"  ✗ Database connection is None")
            return False
        
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False


def check_directories():
    """Verify all required directories exist."""
    print("\n📁 Checking directory structure...")
    
    dirs = [
        "data/checkpoints",
        "data/logs",
        "data/sessions",
        "data/tensorboard",
        "models",
    ]
    
    all_exist = True
    
    for dir_path in dirs:
        p = Path(dir_path)
        if p.exists():
            print(f"  ✓ {dir_path}/")
        else:
            print(f"  ✗ {dir_path}/ (missing)")
            all_exist = False
    
    return all_exist


def check_config():
    """Check if configuration files exist."""
    print("\n⚙️  Checking configuration...")
    
    configs = [
        "config/test_agent.yaml",
        "config/balanced.yaml",
        "config/aggressive.yaml",
    ]
    
    found = 0
    
    for config_path in configs:
        p = Path(config_path)
        if p.exists():
            print(f"  ✓ {config_path}")
            found += 1
        else:
            print(f"  ⚠️  {config_path} (optional)")
    
    return found > 0


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("🚀 CULTIST SIMULATOR AI AGENT - TRAINING READINESS CHECK")
    print("=" * 70)
    
    checks = {
        "Module Imports": check_imports(),
        "Directory Structure": check_directories(),
        "Configuration Files": check_config(),
        "Database Connectivity": check_database(),
        "Game Window Detection": check_game_window(),
        "Screen Capture": check_screen_capture(),
    }
    
    print("\n" + "=" * 70)
    print("📊 RESULTS SUMMARY")
    print("=" * 70)
    
    for check_name, result in checks.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:12} {check_name}")
    
    passed = sum(checks.values())
    total = len(checks)
    
    print("\n" + "=" * 70)
    
    if passed == total:
        print("✅ ALL CHECKS PASSED - Ready for training!")
        print("\nRun your first training session:")
        print("\n  python3 -m src.orchestrator.cli train \\")
        print("    --agent-id test_agent \\")
        print("    --episodes 5 \\")
        print("    --max-actions 10 \\")
        print("    --checkpoint 2 \\")
        print("    --verbose")
        return 0
    else:
        print(f"⚠️  {total - passed} check(s) failed - Fix issues before training")
        print("\nSee TRAINING_SETUP_GUIDE.md for troubleshooting help")
        return 1


if __name__ == "__main__":
    sys.exit(main())
