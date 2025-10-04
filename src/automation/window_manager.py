"""
Window Manager - macOS Window Focus Detection

This module provides functions to check window focus state using Quartz.

Functions:
- check_window_focus(window_name): Check if window has keyboard focus
"""

from typing import Optional

try:
    import Quartz
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID
    )
    QUARTZ_AVAILABLE = True
except ImportError:
    QUARTZ_AVAILABLE = False

from src.lib.logging_config import get_logger

logger = get_logger(__name__)


def check_window_focus(window_name: str) -> bool:
    """
    Check if the specified window currently has keyboard focus.
    
    T064: Window focus verification using Quartz.
    Performance requirement: <5ms.
    
    Args:
        window_name: Name of the window to check (e.g., "Cultist Simulator")
        
    Returns:
        True if window has focus, False otherwise
    """
    if not QUARTZ_AVAILABLE:
        logger.warning("quartz_unavailable", action="focus_check")
        # For testing on non-macOS, return True
        return True
    
    try:
        # Get list of all windows
        window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly,
            kCGNullWindowID
        )
        
        if not window_list:
            logger.warning("no_windows_found")
            return False
        
        # The first window in the list is typically the focused one
        # But we'll check the kCGWindowLayer to be sure (layer 0 = focused)
        for window in window_list:
            # Get window properties
            owner_name = window.get('kCGWindowOwnerName', '')
            window_title = window.get('kCGWindowName', '')
            window_layer = window.get('kCGWindowLayer', 999)
            
            # Check if this is our target window
            if window_name.lower() in owner_name.lower() or \
               window_name.lower() in window_title.lower():
                # Layer 0 means the window is focused
                is_focused = window_layer == 0
                
                logger.debug(
                    "window_focus_check",
                    window_name=window_name,
                    owner=owner_name,
                    title=window_title,
                    layer=window_layer,
                    is_focused=is_focused
                )
                
                return is_focused
        
        # Window not found
        logger.debug(
            "window_not_found",
            window_name=window_name
        )
        return False
        
    except Exception as e:
        logger.error(
            "focus_check_error",
            window_name=window_name,
            error=str(e)
        )
        # Return False on error (safer to assume unfocused)
        return False
