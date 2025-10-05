"""
TensorBoard VS Code Integration

Automatically launches TensorBoard extension in VS Code when training starts.
"""

import os
import subprocess
from pathlib import Path
from src.lib.logging_config import get_logger

logger = get_logger(__name__)


def launch_tensorboard_in_vscode(log_dir: str) -> bool:
    """
    Launch TensorBoard extension in VS Code for the given log directory.
    
    Args:
        log_dir: Path to TensorBoard logs directory
        
    Returns:
        True if successfully launched, False otherwise
    """
    # Make log_dir absolute first (before try block)
    log_path = Path(log_dir).resolve()
    
    try:
        # Ensure directory exists
        log_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Launching TensorBoard in VS Code", log_dir=str(log_path))
        
        # VS Code command to open TensorBoard
        # The extension listens for this and will auto-launch
        command = [
            "code",
            "--command",
            f"python.launchTensorBoard",
            "--log-dir",
            str(log_path)
        ]
        
        # Try to launch via VS Code CLI
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            logger.info(f"TensorBoard launched successfully in VS Code")
            print(f"\n📊 TensorBoard opened in VS Code!")
            print(f"   Log directory: {log_path}")
            print(f"   Look for the 'TensorBoard' tab in VS Code\n")
            return True
        else:
            logger.warning(f"Failed to launch TensorBoard via VS Code CLI", 
                          stderr=result.stderr)
            return _launch_tensorboard_manual(log_path)
            
    except subprocess.TimeoutExpired:
        logger.warning("TensorBoard launch timed out")
        return _launch_tensorboard_manual(log_path)
    except Exception as e:
        logger.error(f"Failed to launch TensorBoard in VS Code", error=str(e))
        return _launch_tensorboard_manual(log_path)


def _launch_tensorboard_manual(log_path: Path) -> bool:
    """
    Fall back to manual instructions if automatic launch fails.
    
    Args:
        log_path: Path to TensorBoard logs
        
    Returns:
        False (indicates manual action needed)
    """
    print("\n" + "="*70)
    print("📊 TENSORBOARD SETUP")
    print("="*70)
    print("\nTo view training metrics in VS Code:")
    print(f"\n1. Open Command Palette (Cmd+Shift+P / Ctrl+Shift+P)")
    print(f"2. Type: 'Python: Launch TensorBoard'")
    print(f"3. Select this directory: {log_path}")
    print(f"\nOr run in terminal:")
    print(f"   tensorboard --logdir {log_path}")
    print(f"   Then open: http://localhost:6006")
    print("="*70 + "\n")
    
    logger.info("Manual TensorBoard instructions provided")
    return False


def create_tensorboard_notice(log_dir: str) -> str:
    """
    Create a notice message about TensorBoard availability.
    
    Args:
        log_dir: Path to TensorBoard logs directory
        
    Returns:
        Formatted notice string
    """
    log_path = Path(log_dir).resolve()
    
    return f"""
╔══════════════════════════════════════════════════════════════════════╗
║                       📊 TENSORBOARD AVAILABLE                        ║
╚══════════════════════════════════════════════════════════════════════╝

Training metrics are being logged to:
  {log_path}

To view in VS Code:
  1. Cmd+Shift+P → "Python: Launch TensorBoard"
  2. Select: {log_path}

Or via browser:
  tensorboard --logdir {log_path}
  http://localhost:6006

Metrics tracked:
  • Episode rewards
  • Episode lengths
  • Learning rate
  • Loss values
  • Action distributions
  • Success rates

╚══════════════════════════════════════════════════════════════════════╝
"""
