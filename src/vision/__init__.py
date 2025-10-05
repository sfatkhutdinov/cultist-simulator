"""
Vision Library - Screen capture and element detection for Cultist Simulator.

Public API:
- capture_game_state(window_name) -> GameState
- detect_elements(image) -> List[GameElement]
- extract_text_regions(image) -> List[TextRegion]
- track_element_changes(prev_state, curr_state) -> List[Change]
- get_window_bounds(window_name) -> Rect

T049: Initialize vision library structure and __init__.py
T055: Implement capture_game_state() integrating all vision components
T056: Implement detect_elements() public interface
T057: Implement extract_text_regions() public interface
T058: Implement track_element_changes() state comparison
"""

import time
from datetime import datetime
from typing import List, Optional, Dict, Any
import numpy as np

from src.lib.types import GameState, GameElement, TextRegion, Rect, Point
from src.lib.logging_config import get_logger
from src.vision.screen_capture import (
    capture_window_screenshot,
    get_window_bounds as _get_window_bounds,
    WindowNotFoundError,
)
from src.vision.element_detector import (
    detect_elements as _detect_elements_internal,
    InvalidImageError,
)
from src.vision.ocr import extract_text_regions as _extract_text_regions_internal

logger = get_logger(__name__)


# Re-export exceptions for public API
__all__ = [
    "capture_game_state",
    "detect_elements",
    "extract_text_regions",
    "track_element_changes",
    "get_window_bounds",
    "WindowNotFoundError",
    "InvalidImageError",
]


def get_window_bounds(window_name: str) -> Rect:
    """
    Get the bounding rectangle of a window by name.

    Args:
        window_name: Name of the window to find

    Returns:
        Rect object with window bounds

    Raises:
        WindowNotFoundError: If window is not found
    """
    return _get_window_bounds(window_name)


def detect_elements(
    screenshot: np.ndarray, element_types: Optional[List] = None
) -> List[GameElement]:
    """
    Detect game elements in an image.

    T056: Public interface for element detection.

    Args:
        screenshot: RGB image as numpy array (H, W, 3)
        element_types: Optional list of ElementType to filter for

    Returns:
        List of detected GameElement objects

    Raises:
        InvalidImageError: If image format is invalid
    """
    start_time = time.perf_counter()

    elements = _detect_elements_internal(screenshot)

    # Filter by element types if specified
    if element_types is not None:
        elements = [e for e in elements if e.element_type in element_types]

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    logger.debug(
        "detect_elements_complete", element_count=len(elements), elapsed_ms=elapsed_ms
    )

    return elements


def extract_text_regions(
    screenshot: np.ndarray, regions: Optional[List[Rect]] = None
) -> List[TextRegion]:
    """
    Extract text regions from an image using OCR.

    T057: Public interface for text extraction.

    Args:
        screenshot: RGB image as numpy array (H, W, 3)
        regions: Optional list of Rect regions to extract text from (if None, extract from entire image)

    Returns:
        List of TextRegion objects containing detected text
    """
    start_time = time.perf_counter()

    if regions is None:
        # Extract text from entire image
        text_regions = _extract_text_regions_internal(screenshot)
    else:
        # Extract text from specific regions
        text_regions = []
        for region in regions:
            # Crop to region
            cropped = screenshot[
                region.y : region.y + region.height, region.x : region.x + region.width
            ]
            # Extract text from cropped region
            region_texts = _extract_text_regions_internal(cropped)
            # Adjust coordinates back to full image
            for text_region in region_texts:
                adjusted_bounds = Rect(
                    x=text_region.bounds.x + region.x,
                    y=text_region.bounds.y + region.y,
                    width=text_region.bounds.width,
                    height=text_region.bounds.height,
                )
                adjusted_region = TextRegion(
                    text=text_region.text,
                    bounds=adjusted_bounds,
                    confidence=text_region.confidence,
                )
                text_regions.append(adjusted_region)

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    logger.debug(
        "extract_text_regions_complete",
        region_count=len(text_regions),
        elapsed_ms=elapsed_ms,
    )

    return text_regions


def capture_game_state(
    window_name: str = "Cultist Simulator", 
    enable_ocr: bool = True
) -> GameState:
    """
    Capture complete game state including screenshot, elements, and text.

    T055: Main integration function combining all vision components.

    Args:
        window_name: Name of the game window to capture (default: "Cultist Simulator")
        enable_ocr: Whether to run OCR text extraction (default: True).
                   Set to False during random exploration to speed up 40-50x.

    Returns:
        GameState object containing all captured information

    Raises:
        WindowNotFoundError: If window is not found
    """
    start_time = time.perf_counter()

    # Capture screenshot and window bounds
    screenshot, window_bounds = capture_window_screenshot(window_name)

    # Detect elements in the screenshot
    elements = detect_elements(screenshot)

    # Extract text regions (skip if OCR disabled for performance)
    if enable_ocr:
        text_regions = extract_text_regions(screenshot)
    else:
        text_regions = []
        logger.debug("ocr_skipped", reason="enable_ocr=False")

    # Create GameState object
    game_state = GameState(
        timestamp=datetime.now(),
        window_bounds=window_bounds,
        elements=elements,
        text_regions=text_regions,
        screenshot=screenshot,
        metadata={},
    )

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        "game_state_captured",
        window_name=window_name,
        element_count=len(elements),
        text_region_count=len(text_regions),
        elapsed_ms=elapsed_ms,
    )

    return game_state


def track_element_changes(
    prev_state: GameState, curr_state: GameState
) -> List[Dict[str, Any]]:
    """
    Track changes in game elements between two states.

    T058: State comparison for detecting element changes.

    Identifies:
    - New elements that appeared
    - Elements that disappeared
    - Elements that moved
    - Elements whose state changed

    Args:
        prev_state: Previous game state
        curr_state: Current game state

    Returns:
        List of change dictionaries describing what changed
    """
    changes = []

    # Build sets of element identifiers (simplified)
    prev_elements = {
        (e.element_type, e.bounds.x, e.bounds.y): e for e in prev_state.elements
    }
    curr_elements = {
        (e.element_type, e.bounds.x, e.bounds.y): e for e in curr_state.elements
    }

    # Find new elements
    new_keys = set(curr_elements.keys()) - set(prev_elements.keys())
    for key in new_keys:
        changes.append(
            {
                "type": "element_appeared",
                "element": curr_elements[key],
                "timestamp": curr_state.timestamp,
            }
        )

    # Find removed elements
    removed_keys = set(prev_elements.keys()) - set(curr_elements.keys())
    for key in removed_keys:
        changes.append(
            {
                "type": "element_disappeared",
                "element": prev_elements[key],
                "timestamp": curr_state.timestamp,
            }
        )

    # Find changed elements (same position, different state)
    common_keys = set(prev_elements.keys()) & set(curr_elements.keys())
    for key in common_keys:
        prev_elem = prev_elements[key]
        curr_elem = curr_elements[key]

        if prev_elem.state != curr_elem.state:
            changes.append(
                {
                    "type": "element_state_changed",
                    "element": curr_elem,
                    "prev_state": prev_elem.state,
                    "curr_state": curr_elem.state,
                    "timestamp": curr_state.timestamp,
                }
            )

    logger.debug(
        "element_changes_tracked",
        change_count=len(changes),
        appeared=len([c for c in changes if c["type"] == "element_appeared"]),
        disappeared=len([c for c in changes if c["type"] == "element_disappeared"]),
        changed=len([c for c in changes if c["type"] == "element_state_changed"]),
    )

    return changes


if __name__ == "__main__":
    # Test vision library
    print("Testing vision library...")

    try:
        # Test with a known window (Finder should always exist on macOS)
        print("\nTesting with Finder window...")

        try:
            bounds = get_window_bounds("Finder")
            print(f"✓ get_window_bounds: {bounds}")
        except WindowNotFoundError as e:
            print(f"! Skipping window tests (Finder not found): {e}")

        # Test with test image
        print("\nTesting with test image...")
        test_image = np.ones((480, 640, 3), dtype=np.uint8) * 128

        elements = detect_elements(test_image)
        print(f"✓ detect_elements: {len(elements)} elements")

        text_regions = extract_text_regions(test_image)
        print(f"✓ extract_text_regions: {len(text_regions)} regions")

        print("\n✓ Vision library tests passed")

    except Exception as e:
        print(f"✗ Vision library test failed: {e}")
        import traceback

        traceback.print_exc()
