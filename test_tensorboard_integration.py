#!/usr/bin/env python3
"""
Test TensorBoard Integration with VS Code

This script tests the automatic TensorBoard launch when training starts.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestrator.tensorboard_vscode import (
    launch_tensorboard_in_vscode,
    create_tensorboard_notice
)


def main():
    print("="*70)
    print("Testing TensorBoard VS Code Integration")
    print("="*70)
    
    # Test log directory
    tensorboard_dir = Path(__file__).parent / "data" / "tensorboard"
    
    print(f"\nTensorBoard directory: {tensorboard_dir}")
    print(f"Directory exists: {tensorboard_dir.exists()}")
    
    # Create directory if needed
    tensorboard_dir.mkdir(parents=True, exist_ok=True)
    
    # Test launch function
    print("\n1. Testing automatic TensorBoard launch...")
    print("-" * 70)
    
    success = launch_tensorboard_in_vscode(str(tensorboard_dir))
    
    if success:
        print("✅ TensorBoard launched successfully!")
        print("\nExpected behavior:")
        print("  - A 'TensorBoard' tab should appear in VS Code")
        print("  - The tab should show the TensorBoard UI")
        print("  - Log directory should be set to:")
        print(f"    {tensorboard_dir}")
    else:
        print("⚠️  Automatic launch failed (see manual instructions above)")
        print("\nThis is expected if:")
        print("  - VS Code CLI is not in PATH")
        print("  - VS Code is not running")
        print("  - TensorBoard extension is not installed")
    
    # Test notice message
    print("\n" + "="*70)
    print("2. Testing notice message generation...")
    print("-" * 70)
    
    notice = create_tensorboard_notice(str(tensorboard_dir))
    print(notice)
    
    print("="*70)
    print("Test complete!")
    print("="*70)


if __name__ == "__main__":
    main()
