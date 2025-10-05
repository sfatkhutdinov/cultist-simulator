"""
Window Manager - macOS Window Focus Detection and Bounds

This module provides functions to check window focus state and get window bounds using Quartz.

Functions:
- check_window_focus(window_name): Check if window has keyboard focus
- get_active_window_bounds(window_name): Get bounds of active window
- is_window_active(window_name): Check if window exists and is focused
"""

from typing import Optional, Tuple

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

from src.lib.types import Rect, Point
from src.lib.logging_config import get_logger

logger = get_logger(__name__)


def check_window_focus(window_name: str) -> bool:
    """
    Check if the specified window currently has keyboard focus.
    
    T064: Window focus verification using Quartz.
    Performance requirement: <10ms (iterates through window list).
    
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


def get_active_window_bounds(window_name: str) -> Optional[Rect]:
    """
    Get the bounds (x, y, width, height) of the active window.
    
    CRITICAL for single-screen setups: This ensures the agent only
    interacts within the game window boundaries.
    
    Args:
        window_name: Name of the window (e.g., "Cultist Simulator")
        
    Returns:
        Rect with window bounds, or None if window not found/focused
    """
    if not QUARTZ_AVAILABLE:
        logger.warning("quartz_unavailable", action="get_bounds")
        # Return a safe default for testing
        return Rect(x=0, y=0, width=1920, height=1080)
    
    try:
        window_list = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly,
            kCGNullWindowID
        )
        
        if not window_list:
            logger.warning("no_windows_found")
            return None
        
        # Find the target window
        for window in window_list:
            owner_name = window.get('kCGWindowOwnerName', '')
            window_title = window.get('kCGWindowName', '')
            window_layer = window.get('kCGWindowLayer', 999)
            
            # Check if this is our target window and it's focused
            if (window_name.lower() in owner_name.lower() or \
                window_name.lower() in window_title.lower()) and \
                window_layer == 0:
                
                # Get window bounds
                bounds_dict = window.get('kCGWindowBounds', {})
                x = int(bounds_dict.get('X', 0))
                y = int(bounds_dict.get('Y', 0))
                width = int(bounds_dict.get('Width', 0))
                height = int(bounds_dict.get('Height', 0))
                
                bounds = Rect(x=x, y=y, width=width, height=height)
                
                logger.info(
                    "active_window_bounds",
                    window_name=window_name,
                    bounds=str(bounds)
                )
                
                return bounds
        
        # Window not found or not focused
        logger.warning(
            "window_not_active",
            window_name=window_name,
            message="Window not found or not focused"
        )
        return None
        
    except Exception as e:
        logger.error(
            "get_bounds_error",
            window_name=window_name,
            error=str(e)
        )
        return None


def is_window_active(window_name: str) -> bool:
    """
    Check if window exists and is currently the active/focused window.
    
    SAFETY CRITICAL: For single-screen setups, this ensures we don't
    accidentally interact with the wrong application.
    
    Args:
        window_name: Name of the window to check
        
    Returns:
        True if window is active and focused, False otherwise
    """
    bounds = get_active_window_bounds(window_name)
    return bounds is not None


def require_active_window(window_name: str) -> Rect:
    """
    Require that the specified window is active and return its bounds.
    
    SAFETY CRITICAL: Call this before ANY automation action to ensure
    we're only interacting with the game window.
    
    Args:
        window_name: Name of the required window
        
    Returns:
        Rect with window bounds
        
    Raises:
        RuntimeError: If window is not active/focused
    """
    bounds = get_active_window_bounds(window_name)
    
    if bounds is None:
        error_msg = (
            f"Window '{window_name}' is not active! "
            f"Please focus the game window before running the agent. "
            f"This is required for single-screen setups to prevent "
            f"accidental interaction with other applications."
        )
        logger.error("window_not_active_required", window_name=window_name)
        raise RuntimeError(error_msg)
    
    return bounds