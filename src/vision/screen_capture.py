"""
Screen capture functionality for macOS using Quartz.
T050: Implement screen capture using Quartz.
T051: Implement get_window_bounds() for game window location.
"""

import Quartz
import Quartz.CoreGraphics as CG
import numpy as np
from typing import Optional, Tuple
from src.lib.types import Rect, Point
from src.lib.logging_config import get_logger


logger = get_logger(__name__)


class WindowNotFoundError(Exception):
    """Raised when the specified window cannot be found."""
    pass


def get_window_bounds(window_name: str) -> Rect:
    """
    Get the bounding rectangle of a window by name.
    
    Args:
        window_name: Name of the window to find
    
    Returns:
        Rect object with window bounds
    
    Raises:
        WindowNotFoundError: If window not found
    """
    window_list = CG.CGWindowListCopyWindowInfo(
        CG.kCGWindowListOptionOnScreenOnly,
        CG.kCGNullWindowID
    )
    
    for window in window_list:
        name = window.get('kCGWindowName', '')
        owner = window.get('kCGWindowOwnerName', '')
        
        # Match either window name or owner name
        if window_name.lower() in name.lower() or window_name.lower() in owner.lower():
            bounds = window['kCGWindowBounds']
            
            logger.debug(
                "window_found",
                window_name=window_name,
                x=bounds['X'],
                y=bounds['Y'],
                width=bounds['Width'],
                height=bounds['Height']
            )
            
            return Rect(
                x=int(bounds['X']),
                y=int(bounds['Y']),
                width=int(bounds['Width']),
                height=int(bounds['Height'])
            )
    
    logger.error("window_not_found", window_name=window_name)
    raise WindowNotFoundError(f"Window '{window_name}' not found")


def capture_window_screenshot(window_name: str) -> Tuple[np.ndarray, Rect]:
    """
    Capture screenshot of a specific window.
    
    Args:
        window_name: Name of the window to capture
    
    Returns:
        Tuple of (screenshot as np.ndarray, window bounds)
    
    Raises:
        WindowNotFoundError: If window not found
    """
    # Get window bounds first
    bounds = get_window_bounds(window_name)
    
    # Capture the region
    screenshot = capture_screen_region(bounds)
    
    logger.debug(
        "window_screenshot_captured",
        window_name=window_name,
        width=screenshot.shape[1],
        height=screenshot.shape[0],
        channels=screenshot.shape[2] if len(screenshot.shape) > 2 else 1
    )
    
    return screenshot, bounds


def capture_screen_region(region: Rect) -> np.ndarray:
    """
    Capture a region of the screen.
    
    Args:
        region: Screen region to capture
        
    Returns:
        Screenshot as numpy array (RGB)
    """
    from PIL import ImageGrab
    
    # Capture full screen
    screenshot = ImageGrab.grab()
    
    # Crop to requested region
    box = (region.x, region.y, region.x + region.width, region.y + region.height)
    cropped = screenshot.crop(box)
    
    # Convert to RGB if needed (removes alpha channel)
    if cropped.mode != 'RGB':
        cropped = cropped.convert('RGB')
    
    # Convert to numpy array (RGB)
    image_array = np.array(cropped)
    
    logger.debug(
        "screen_region_captured",
        width=region.width,
        height=region.height,
        shape=image_array.shape
    )
    
    return image_array


def capture_full_screen() -> np.ndarray:
    """
    Capture the entire screen.
    
    Returns:
        Screenshot as np.ndarray (H, W, 3) in RGB format
    """
    # Get main display bounds
    display_bounds = CG.CGDisplayBounds(CG.CGMainDisplayID())
    
    region = Rect(
        x=int(display_bounds.origin.x),
        y=int(display_bounds.origin.y),
        width=int(display_bounds.size.width),
        height=int(display_bounds.size.height)
    )
    
    return capture_screen_region(region)


if __name__ == "__main__":
    # Test screen capture functionality
    print("Testing screen capture...")
    
    try:
        # Test full screen capture
        screen = capture_full_screen()
        print(f"✓ Full screen captured: {screen.shape}")
        
        # Test window bounds (will fail if window doesn't exist)
        try:
            bounds = get_window_bounds("Finder")
            print(f"✓ Finder window found: {bounds}")
            
            # Capture Finder window
            screenshot, _ = capture_window_screenshot("Finder")
            print(f"✓ Finder screenshot captured: {screenshot.shape}")
        except WindowNotFoundError as e:
            print(f"! Window test skipped: {e}")
        
        print("\n✓ Screen capture tests passed")
        
    except Exception as e:
        print(f"✗ Screen capture test failed: {e}")
        import traceback
        traceback.print_exc()
