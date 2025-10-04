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
    Capture a specific region of the screen.
    
    Args:
        region: Rectangle defining the region to capture
    
    Returns:
        Screenshot as np.ndarray (H, W, 3) in RGB format
    """
    # Create CGRect for the region
    cg_rect = CG.CGRectMake(region.x, region.y, region.width, region.height)
    
    # Capture the image
    image_ref = CG.CGWindowListCreateImage(
        cg_rect,
        CG.kCGWindowListOptionOnScreenBelowWindow,
        CG.kCGNullWindowID,
        CG.kCGWindowImageDefault
    )
    
    if image_ref is None:
        logger.error("screen_capture_failed", region=str(region))
        raise RuntimeError(f"Failed to capture screen region: {region}")
    
    # Get image properties
    width = CG.CGImageGetWidth(image_ref)
    height = CG.CGImageGetHeight(image_ref)
    bytes_per_row = CG.CGImageGetBytesPerRow(image_ref)
    
    # Create bitmap context and extract pixel data
    color_space = CG.CGColorSpaceCreateDeviceRGB()
    bitmap_context = CG.CGBitmapContextCreate(
        None,
        width,
        height,
        8,  # bits per component
        bytes_per_row,
        color_space,
        CG.kCGImageAlphaPremultipliedLast | CG.kCGBitmapByteOrder32Big
    )
    
    # Draw image into context
    CG.CGContextDrawImage(
        bitmap_context,
        CG.CGRectMake(0, 0, width, height),
        image_ref
    )
    
    # Get pixel data
    pixel_data = CG.CGBitmapContextGetData(bitmap_context)
    
    # Convert to numpy array
    # Note: Quartz returns RGBA, we want RGB
    # Convert objc.varlist to bytes first
    pixel_bytes = bytes(pixel_data)
    image_array = np.frombuffer(pixel_bytes, dtype=np.uint8)
    image_array = image_array.reshape((height, width, 4))
    
    # Convert RGBA to RGB
    image_rgb = image_array[:, :, :3].copy()
    
    logger.debug(
        "screen_region_captured",
        width=width,
        height=height,
        shape=image_rgb.shape
    )
    
    return image_rgb


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
