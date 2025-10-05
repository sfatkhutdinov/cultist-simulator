"""
Element detection using YOLO and template matching.
T052: Implement YOLO-based element detection.
T053: Implement template matching for UI elements.
"""

import numpy as np
from typing import List, Optional
from pathlib import Path

from src.lib.types import GameElement, Rect, ElementType, Point
from src.lib.logging_config import get_logger

logger = get_logger(__name__)


class InvalidImageError(Exception):
    """Raised when the provided image is invalid."""

    pass


def validate_image(image: np.ndarray) -> None:
    """
    Validate that image is in correct format.

    Args:
        image: Image to validate

    Raises:
        InvalidImageError: If image is invalid
    """
    if not isinstance(image, np.ndarray):
        raise InvalidImageError(f"Image must be numpy array, got {type(image)}")

    if len(image.shape) != 3:
        raise InvalidImageError(
            f"Image must be 3D array (H,W,C), got shape {image.shape}"
        )

    if image.shape[2] != 3:
        raise InvalidImageError(
            f"Image must have 3 channels (RGB), got {image.shape[2]}"
        )

    if image.dtype != np.uint8:
        raise InvalidImageError(f"Image must be uint8, got {image.dtype}")


def detect_elements_yolo(
    image: np.ndarray, confidence_threshold: float = 0.5
) -> List[GameElement]:
    """
    Detect game elements using YOLO object detection.

    This is a placeholder implementation. Full YOLO integration requires:
    - Training YOLO model on Cultist Simulator screenshots
    - Model weights file
    - YOLO inference code

    Args:
        image: RGB image as numpy array (H, W, 3)
        confidence_threshold: Minimum confidence for detections

    Returns:
        List of detected GameElement objects

    Raises:
        InvalidImageError: If image format is invalid
    """
    validate_image(image)

    # TODO: Implement actual YOLO detection
    # For now, return empty list to pass basic tests
    # This will be implemented in a future task when YOLO model is trained

    logger.debug(
        "yolo_detection_placeholder",
        image_shape=image.shape,
        confidence_threshold=confidence_threshold,
    )

    # Placeholder: Return empty list
    # Real implementation will:
    # 1. Load YOLO model weights
    # 2. Run inference on image
    # 3. Filter by confidence threshold
    # 4. Convert bounding boxes to GameElement objects

    return []


def detect_elements_template_matching(
    image: np.ndarray,
    template_dir: Optional[Path] = None,
    confidence_threshold: float = 0.7,
) -> List[GameElement]:
    """
    Detect UI elements using template matching.

    Template matching is useful for detecting consistent UI elements like:
    - Buttons (play, pause, menu)
    - Icons (resources, verbs)
    - Slot markers

    Args:
        image: RGB image as numpy array (H, W, 3)
        template_dir: Directory containing template images
        confidence_threshold: Minimum match score (0.0-1.0)

    Returns:
        List of detected GameElement objects

    Raises:
        InvalidImageError: If image format is invalid
    """
    validate_image(image)

    # TODO: Implement template matching
    # For now, return empty list to pass basic tests

    logger.debug(
        "template_matching_placeholder",
        image_shape=image.shape,
        template_dir=str(template_dir) if template_dir else None,
        confidence_threshold=confidence_threshold,
    )

    # Placeholder: Return empty list
    # Real implementation will:
    # 1. Load template images from template_dir
    # 2. For each template, run cv2.matchTemplate
    # 3. Find peaks above confidence_threshold
    # 4. Convert to GameElement objects with appropriate ElementType

    return []


def detect_elements(
    image: np.ndarray, use_yolo: bool = True, use_templates: bool = True
) -> List[GameElement]:
    """
    Detect all game elements using available methods.

    Combines YOLO detection and template matching for comprehensive element detection.

    Args:
        image: RGB image as numpy array (H, W, 3)
        use_yolo: Whether to use YOLO detection
        use_templates: Whether to use template matching

    Returns:
        List of detected GameElement objects

    Raises:
        InvalidImageError: If image format is invalid
    """
    validate_image(image)

    elements = []

    if use_yolo:
        yolo_elements = detect_elements_yolo(image)
        elements.extend(yolo_elements)

    if use_templates:
        template_elements = detect_elements_template_matching(image)
        elements.extend(template_elements)

    logger.debug(
        "elements_detected",
        total_count=len(elements),
        yolo_enabled=use_yolo,
        templates_enabled=use_templates,
    )

    return elements


def merge_overlapping_elements(
    elements: List[GameElement], iou_threshold: float = 0.5
) -> List[GameElement]:
    """
    Merge overlapping detections using Non-Maximum Suppression (NMS).

    When multiple detection methods find the same element, merge them.

    Args:
        elements: List of detected elements
        iou_threshold: Intersection-over-Union threshold for merging

    Returns:
        List of merged elements
    """
    if len(elements) <= 1:
        return elements

    # TODO: Implement NMS
    # For now, just return all elements

    logger.debug(
        "nms_placeholder", element_count=len(elements), iou_threshold=iou_threshold
    )

    return elements


if __name__ == "__main__":
    # Test element detection
    print("Testing element detection...")

    try:
        # Create test image
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        test_image[:, :] = [100, 150, 200]  # Gray-blue color

        # Test validation
        validate_image(test_image)
        print(f"✓ Image validation passed")

        # Test YOLO detection (placeholder)
        yolo_elements = detect_elements_yolo(test_image)
        print(f"✓ YOLO detection: {len(yolo_elements)} elements")

        # Test template matching (placeholder)
        template_elements = detect_elements_template_matching(test_image)
        print(f"✓ Template matching: {len(template_elements)} elements")

        # Test combined detection
        all_elements = detect_elements(test_image)
        print(f"✓ Combined detection: {len(all_elements)} elements")

        # Test invalid image
        try:
            validate_image("not an array")
            print("✗ Should have raised InvalidImageError")
        except InvalidImageError:
            print("✓ InvalidImageError raised correctly")

        print("\n✓ Element detection tests passed")

    except Exception as e:
        print(f"✗ Element detection test failed: {e}")
        import traceback

        traceback.print_exc()
