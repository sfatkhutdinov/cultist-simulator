"""
macOS Permissions Checker

T122: Check required macOS permissions on startup.

Verifies:
- Screen Recording permission (for screenshot capture)
- Accessibility permission (for input simulation)
- Provides helpful error messages and setup instructions
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, Tuple

from src.lib.logging_config import get_logger

logger = get_logger(__name__)


def check_screen_recording_permission() -> bool:
    """
    Check if screen recording permission is granted.
    
    Returns:
        True if permission granted, False otherwise
    """
    try:
        # Try to capture a small screenshot using screencapture
        result = subprocess.run(
            ['screencapture', '-x', '-R', '0,0,1,1', '/tmp/test_screenshot.png'],
            capture_output=True,
            timeout=2
        )
        
        # Check if file was created
        test_file = Path('/tmp/test_screenshot.png')
        has_permission = test_file.exists()
        
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        
        return has_permission
        
    except Exception as e:
        logger.error(
            "screen_recording_check_failed",
            error=str(e)
        )
        return False


def check_accessibility_permission() -> bool:
    """
    Check if accessibility permission is granted.
    
    Note: This is an approximate check. macOS doesn't provide a direct
    API to query accessibility permissions for the current process.
    
    Returns:
        True if likely granted, False if likely denied
    """
    try:
        # Try using PyObjC to check accessibility
        from Quartz import CGEventSourceCreate, kCGEventSourceStateHIDSystemState
        
        # If this succeeds, accessibility is likely granted
        source = CGEventSourceCreate(kCGEventSourceStateHIDSystemState)
        return source is not None
        
    except Exception as e:
        logger.warning(
            "accessibility_check_uncertain",
            error=str(e),
            message="Unable to definitively check accessibility permission"
        )
        # Return True to not block startup, but warn user
        return True


def get_permission_instructions() -> Dict[str, str]:
    """
    Get instructions for granting required permissions.
    
    Returns:
        Dictionary with permission names and setup instructions
    """
    return {
        "screen_recording": """
Screen Recording Permission Required:
1. Open System Settings > Privacy & Security > Screen Recording
2. Enable permission for Terminal (or your IDE if running from IDE)
3. Restart this application

If using an IDE (VS Code, PyCharm, etc.), add the IDE to Screen Recording permissions.
        """.strip(),
        
        "accessibility": """
Accessibility Permission Required:
1. Open System Settings > Privacy & Security > Accessibility
2. Enable permission for Terminal (or your IDE if running from IDE)
3. Restart this application

This permission is required for simulating keyboard and mouse input.
        """.strip()
    }


def check_all_permissions() -> Tuple[bool, Dict[str, bool]]:
    """
    Check all required macOS permissions.
    
    Returns:
        Tuple of (all_granted, permission_status_dict)
    """
    logger.info("checking_macos_permissions")
    
    permissions = {
        "screen_recording": check_screen_recording_permission(),
        "accessibility": check_accessibility_permission()
    }
    
    all_granted = all(permissions.values())
    
    logger.info(
        "permissions_check_complete",
        all_granted=all_granted,
        permissions=permissions
    )
    
    return all_granted, permissions


def require_permissions() -> None:
    """
    Check permissions and exit with instructions if not granted.
    
    Call this at application startup to ensure required permissions
    are granted before proceeding.
    """
    all_granted, permissions = check_all_permissions()
    
    if all_granted:
        logger.info("all_permissions_granted")
        return
    
    # Print helpful error messages
    print("\n" + "=" * 70)
    print("ERROR: Required macOS Permissions Not Granted")
    print("=" * 70 + "\n")
    
    instructions = get_permission_instructions()
    
    if not permissions.get("screen_recording"):
        print("❌ Screen Recording Permission: DENIED\n")
        print(instructions["screen_recording"])
        print("\n")
    else:
        print("✅ Screen Recording Permission: GRANTED\n")
    
    if not permissions.get("accessibility"):
        print("❌ Accessibility Permission: DENIED\n")
        print(instructions["accessibility"])
        print("\n")
    else:
        print("✅ Accessibility Permission: GRANTED\n")
    
    print("=" * 70)
    print("Please grant the required permissions and restart the application.")
    print("=" * 70 + "\n")
    
    logger.error(
        "missing_permissions_exiting",
        permissions=permissions
    )
    
    sys.exit(1)


def print_permission_status() -> None:
    """Print current permission status (for debugging)."""
    all_granted, permissions = check_all_permissions()
    
    print("\nmacOS Permissions Status:")
    print("-" * 40)
    
    for name, granted in permissions.items():
        status = "✅ GRANTED" if granted else "❌ DENIED"
        print(f"{name.replace('_', ' ').title()}: {status}")
    
    print("-" * 40)
    
    if all_granted:
        print("All permissions granted! ✅\n")
    else:
        print("Some permissions missing! ❌\n")
