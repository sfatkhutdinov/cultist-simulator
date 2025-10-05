"""
OCR text extraction using EasyOCR.
T054: Implement OCR text extraction using EasyOCR.
"""

import numpy as np
import warnings
from typing import List, Optional
import easyocr

from src.lib.types import TextRegion, Rect
from src.lib.logging_config import get_logger

# Suppress PyTorch MPS pin_memory warning on macOS
warnings.filterwarnings("ignore", message=".*pin_memory.*not supported on MPS.*")

logger = get_logger(__name__)


# Global OCR reader instance (initialized lazily)
_ocr_reader: Optional[easyocr.Reader] = None


def get_ocr_reader() -> easyocr.Reader:
    """
    Get or initialize the EasyOCR reader.

    Lazy initialization to avoid loading model until needed.

    Returns:
        EasyOCR Reader instance
    """
    global _ocr_reader

    if _ocr_reader is None:
        logger.info("Initializing EasyOCR reader (this may take a moment)...")
        _ocr_reader = easyocr.Reader(["en"], gpu=False)
        logger.info("EasyOCR reader initialized")

    return _ocr_reader


def extract_text_regions(
    image: np.ndarray, confidence_threshold: float = 0.6
) -> List[TextRegion]:
    """
    Extract text regions from an image using OCR.

    Args:
        image: RGB image as numpy array (H, W, 3)
        confidence_threshold: Minimum confidence for text detection (0.0-1.0)

    Returns:
        List of TextRegion objects containing detected text
    """
    if not isinstance(image, np.ndarray):
        raise ValueError(f"Image must be numpy array, got {type(image)}")

    if len(image.shape) != 3 or image.shape[2] != 3:
        raise ValueError(f"Image must be RGB (H, W, 3), got shape {image.shape}")

    reader = get_ocr_reader()

    # Run OCR detection
    # EasyOCR returns: [bbox, text, confidence]
    # bbox is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    results = reader.readtext(image)

    text_regions = []

    for bbox, text, confidence in results:
        # Filter by confidence threshold
        if confidence < confidence_threshold:
            continue

        # Extract bounding box coordinates
        # bbox is a list of 4 corner points
        xs = [point[0] for point in bbox]
        ys = [point[1] for point in bbox]

        x = int(min(xs))
        y = int(min(ys))
        width = int(max(xs) - min(xs))
        height = int(max(ys) - min(ys))

        rect = Rect(x=x, y=y, width=width, height=height)

        region = TextRegion(text=text, bounds=rect, confidence=float(confidence))

        text_regions.append(region)

    logger.debug(
        "text_extraction_complete",
        regions_found=len(text_regions),
        threshold=confidence_threshold,
    )

    return text_regions


def extract_text_from_region(
    image: np.ndarray, region: Rect, confidence_threshold: float = 0.6
) -> Optional[str]:
    """
    Extract text from a specific region of an image.

    Args:
        image: RGB image as numpy array (H, W, 3)
        region: Rectangle defining the region to extract from
        confidence_threshold: Minimum confidence for text detection

    Returns:
        Extracted text or None if no text found
    """
    # Crop image to region
    cropped = image[
        region.y : region.y + region.height, region.x : region.x + region.width
    ]

    # Extract text from cropped region
    text_regions = extract_text_regions(cropped, confidence_threshold)

    if not text_regions:
        return None

    # Concatenate all text (sorted by y-coordinate for reading order)
    text_regions.sort(key=lambda r: r.bounds.y)
    text = " ".join(r.text for r in text_regions)

    return text


if __name__ == "__main__":
    # Test OCR functionality
    print("Testing OCR...")

    try:
        # Create test image with some content
        test_image = np.ones((100, 300, 3), dtype=np.uint8) * 255

        # Test basic extraction (will return empty on blank image)
        regions = extract_text_regions(test_image)
        print(f"✓ Text extraction on blank image: {len(regions)} regions")

        # Test region extraction
        test_region = Rect(x=10, y=10, width=100, height=50)
        text = extract_text_from_region(test_image, test_region)
        print(f"✓ Region text extraction: {text}")

        print("\n✓ OCR tests passed")

    except Exception as e:
        print(f"✗ OCR test failed: {e}")
        import traceback

        traceback.print_exc()
