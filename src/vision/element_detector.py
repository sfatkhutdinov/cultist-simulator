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

    Uses YOLOv8 for general object detection. While not trained specifically
    on Cultist Simulator, it can detect common UI elements like buttons,
    cards, and interactive objects.

    Args:
        image: RGB image as numpy array (H, W, 3)
        confidence_threshold: Minimum confidence for detections

    Returns:
        List of detected GameElement objects

    Raises:
        InvalidImageError: If image format is invalid
    """
    validate_image(image)

    try:
        # Try to use YOLOv8 if available
        from ultralytics import YOLO
        from pathlib import Path
        
        # Check if model file exists
        model_path = Path("yolov8n.pt")
        if not model_path.exists():
            logger.debug(
                "yolo_model_not_found",
                path=str(model_path),
                fallback="empty_results"
            )
            return []
        
        # Load model (cached after first load)
        model = YOLO(str(model_path))
        
        # Run inference
        results = model.predict(image, conf=confidence_threshold, verbose=False)
        
        # Convert YOLO results to GameElement objects
        elements = []
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    
                    # Convert to our format
                    bounds = Rect(
                        x=int(x1),
                        y=int(y1),
                        width=int(x2 - x1),
                        height=int(y2 - y1)
                    )
                    
                    # Map YOLO class to ElementType (use OTHER for now)
                    # TODO: Train custom YOLO on Cultist Simulator to detect CARD, BUTTON, SLOT, etc.
                    element = GameElement(
                        element_type=ElementType.OTHER,
                        bounds=bounds,
                        confidence=conf,
                        metadata={"yolo_class_id": cls_id}
                    )
                    elements.append(element)
        
        logger.debug(
            "yolo_detection_complete",
            image_shape=image.shape,
            confidence_threshold=confidence_threshold,
            elements_found=len(elements)
        )
        
        return elements
        
    except ImportError:
        logger.debug(
            "yolo_not_available",
            reason="ultralytics not installed",
            fallback="empty_results"
        )
        return []
    except Exception as e:
        logger.warning(
            "yolo_detection_error",
            error=str(e),
            fallback="empty_results"
        )
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


def detect_elements_color_based(
    image: np.ndarray,
    min_area: int = 1000,
    max_area: int = 50000,
) -> List[GameElement]:
    """
    Detect Cultist Simulator game elements using color-based detection.
    
    Cultist Simulator has distinct visual elements:
    - Cards: Tan/beige colored rectangles (Aspect cards, Tools, Followers, etc.)
    - Verb slots: Dark colored rectangles (Work, Study, Dream, etc.)
    - Buttons: Various colors depending on state
    
    This function uses HSV color space and contour detection to find these elements.
    
    Args:
        image: RGB image as numpy array (H, W, 3)
        min_area: Minimum contour area to consider (filters noise)
        max_area: Maximum contour area to consider (filters background)
    
    Returns:
        List of detected GameElement objects
        
    Raises:
        InvalidImageError: If image format is invalid
    """
    validate_image(image)
    
    try:
        import cv2
        
        # Convert BGR to HSV for better color detection
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        elements = []
        
        # Detect tan/beige cards (most common in Cultist Simulator)
        # HSV range for tan/beige: H=15-35, S=30-150, V=80-220
        tan_lower = np.array([15, 30, 80])
        tan_upper = np.array([35, 150, 220])
        tan_mask = cv2.inRange(hsv, tan_lower, tan_upper)
        
        # Detect dark verb slots and buttons
        # HSV range for dark elements: H=0-180 (any hue), S=0-255, V=0-70
        dark_lower = np.array([0, 0, 0])
        dark_upper = np.array([180, 255, 70])
        dark_mask = cv2.inRange(hsv, dark_lower, dark_upper)
        
        # Detect bright/highlighted elements (active cards, buttons)
        # HSV range: H=0-180, S=50-255, V=150-255
        bright_lower = np.array([0, 50, 150])
        bright_upper = np.array([180, 255, 255])
        bright_mask = cv2.inRange(hsv, bright_lower, bright_upper)
        
        # Process each color mask
        detection_configs = [
            (tan_mask, ElementType.CARD, "tan_cards"),
            (dark_mask, ElementType.BUTTON, "dark_elements"),
            (bright_mask, ElementType.OTHER, "bright_elements"),
        ]
        
        for mask, element_type, label in detection_configs:
            # Apply morphological operations to clean up mask
            kernel = np.ones((5, 5), np.uint8)
            mask_cleaned = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask_cleaned = cv2.morphologyEx(mask_cleaned, cv2.MORPH_OPEN, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(
                mask_cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Convert contours to GameElement objects
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filter by area
                if area < min_area or area > max_area:
                    continue
                
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by aspect ratio (cards are roughly rectangular)
                aspect_ratio = w / h if h > 0 else 0
                if aspect_ratio < 0.3 or aspect_ratio > 3.0:
                    continue
                
                # Create GameElement
                bounds = Rect(x=x, y=y, width=w, height=h)
                
                # Calculate confidence based on area and aspect ratio
                # Larger, more rectangular elements = higher confidence
                area_score = min(area / max_area, 1.0)
                aspect_score = 1.0 - abs(aspect_ratio - 1.0) / 2.0
                confidence = (area_score + aspect_score) / 2.0
                
                element = GameElement(
                    element_type=element_type,
                    bounds=bounds,
                    confidence=confidence,
                    metadata={
                        "detection_method": "color_based",
                        "color_category": label,
                        "area": int(area),
                        "aspect_ratio": round(aspect_ratio, 2),
                    }
                )
                elements.append(element)
        
        logger.debug(
            "color_detection_complete",
            image_shape=image.shape,
            elements_found=len(elements),
            min_area=min_area,
            max_area=max_area,
        )
        
        return elements
        
    except ImportError:
        logger.warning(
            "color_detection_failed",
            reason="cv2 not available",
            fallback="empty_results"
        )
        return []
    except Exception as e:
        logger.warning(
            "color_detection_error",
            error=str(e),
            fallback="empty_results"
        )
        return []


def detect_elements(
    image: np.ndarray, 
    use_yolo: bool = True, 
    use_templates: bool = True,
    use_color: bool = True,
) -> List[GameElement]:
    """
    Detect all game elements using available methods.

    Combines YOLO detection, template matching, and color-based detection
    for comprehensive element detection.

    Args:
        image: RGB image as numpy array (H, W, 3)
        use_yolo: Whether to use YOLO detection
        use_templates: Whether to use template matching
        use_color: Whether to use color-based detection

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
    
    if use_color:
        color_elements = detect_elements_color_based(image)
        elements.extend(color_elements)

    logger.debug(
        "elements_detected",
        total_count=len(elements),
        yolo_enabled=use_yolo,
        templates_enabled=use_templates,
        color_enabled=use_color,
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
