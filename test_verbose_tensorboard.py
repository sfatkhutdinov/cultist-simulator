#!/usr/bin/env python3
"""
Test script for verbose logging and TensorBoard Safari integration.
Tests the new CLI features without actually running training.
"""

import sys
import subprocess
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestrator.cli import launch_tensorboard_in_safari, cleanup_tensorboard


def test_tensorboard_launch():
    """Test TensorBoard launching in Safari."""
    print("="*60)
    print("Testing TensorBoard Launch in Safari")
    print("="*60)
    
    # Create test tensorboard directory
    tensorboard_dir = Path(__file__).parent / "data" / "tensorboard"
    tensorboard_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a dummy log file so TensorBoard has something to read
    test_log_dir = tensorboard_dir / "test_run"
    test_log_dir.mkdir(exist_ok=True)
    
    try:
        # Test launching TensorBoard
        print("\n1. Testing TensorBoard launch...")
        process = launch_tensorboard_in_safari(tensorboard_dir, verbose=True)
        
        print("\n2. TensorBoard should be running in Safari now")
        print("   Check Safari - you should see TensorBoard at http://localhost:6006")
        
        # Keep it running for a bit
        print("\n3. Keeping TensorBoard running for 5 seconds...")
        time.sleep(5)
        
        # Check if process is still alive
        if process.poll() is None:
            print("✓ TensorBoard process is still running")
        else:
            print("✗ TensorBoard process has stopped")
            return False
        
        # Test cleanup
        print("\n4. Testing cleanup...")
        cleanup_tensorboard()
        time.sleep(2)
        
        if process.poll() is not None:
            print("✓ TensorBoard process stopped successfully")
        else:
            print("✗ TensorBoard process still running after cleanup")
            process.kill()
            return False
        
        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        cleanup_tensorboard()
        return False


def test_cli_help():
    """Test CLI help to ensure new flags are present."""
    print("\n" + "="*60)
    print("Testing CLI Help (checking for --verbose flag)")
    print("="*60 + "\n")
    
    result = subprocess.run(
        ["python", "-m", "src.orchestrator.cli", "train", "--help"],
        capture_output=True,
        text=True
    )
    
    if "--verbose" in result.stdout and "-v" in result.stdout:
        print("✓ --verbose flag found in CLI help")
        return True
    else:
        print("✗ --verbose flag not found in CLI help")
        print("\nHelp output:")
        print(result.stdout)
        return False


if __name__ == "__main__":
    print("Testing Verbose Logging and TensorBoard Safari Integration\n")
    
    # Test 1: CLI help
    test1_passed = test_cli_help()
    
    # Test 2: TensorBoard launch
    print("\n")
    test2_passed = test_tensorboard_launch()
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"CLI Help Test: {'✓ PASSED' if test1_passed else '✗ FAILED'}")
    print(f"TensorBoard Launch Test: {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed")
        sys.exit(1)
