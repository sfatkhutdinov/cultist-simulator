# Vision API

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

**Module**: `src.vision`  
**Generated**: 2025-10-04 22:36:32

---

## Table of Contents

- [Functions](#functions)
- [Classes](#classes)

---

## Functions


### `capture_game_state(window_name: str = 'Cultist Simulator') -> src.lib.types.GameState`

Capture complete game state including screenshot, elements, and text.

T055: Main integration function combining all vision components.

Args:
    window_name: Name of the game window to capture (default: "Cultist Simulator")
    
Returns:
    GameState object containing all captured information
    
Raises:
    WindowNotFoundError: If window is not found

---

### `capture_window_screenshot(window_name: str) -> Tuple[numpy.ndarray, src.lib.types.Rect]`

Capture screenshot of a specific window.

Args:
    window_name: Name of the window to capture

Returns:
    Tuple of (screenshot as np.ndarray, window bounds)

Raises:
    WindowNotFoundError: If window not found

---

### `detect_elements(screenshot: numpy.ndarray, element_types: Optional[List] = None) -> List[src.lib.types.GameElement]`

Detect game elements in an image.

T056: Public interface for element detection.

Args:
    screenshot: RGB image as numpy array (H, W, 3)
    element_types: Optional list of ElementType to filter for
    
Returns:
    List of detected GameElement objects
    
Raises:
    InvalidImageError: If image format is invalid

---

### `extract_text_regions(screenshot: numpy.ndarray, regions: Optional[List[src.lib.types.Rect]] = None) -> List[src.lib.types.TextRegion]`

Extract text regions from an image using OCR.

T057: Public interface for text extraction.

Args:
    screenshot: RGB image as numpy array (H, W, 3)
    regions: Optional list of Rect regions to extract text from (if None, extract from entire image)
    
Returns:
    List of TextRegion objects containing detected text

---

### `get_logger(name: str = None)`

Get a logger instance.

Args:
    name: Optional logger name (typically __name__)

Returns:
    Structlog logger instance

---

### `get_window_bounds(window_name: str) -> src.lib.types.Rect`

Get the bounding rectangle of a window by name.

Args:
    window_name: Name of the window to find
    
Returns:
    Rect object with window bounds
    
Raises:
    WindowNotFoundError: If window is not found

---

### `track_element_changes(prev_state: src.lib.types.GameState, curr_state: src.lib.types.GameState) -> List[Dict[str, Any]]`

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

---

## Classes


### `class GameElement`

Represents a detected UI element in the game.
T040: Implement GameElement entity.

**Methods:**


#### `__init__(self, element_type: src.lib.types.ElementType, bounds: src.lib.types.Rect, confidence: float, text: Optional[str] = None, state: Optional[str] = None, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class GameState`

Complete snapshot of the game state at a point in time.
T039: Implement GameState entity.

**Methods:**


#### `__init__(self, timestamp: datetime.datetime, window_bounds: src.lib.types.Rect, elements: List[src.lib.types.GameElement], text_regions: List[src.lib.types.TextRegion], screenshot: Optional[numpy.ndarray] = None, metadata: Dict[str, Any] = <factory>) -> None`

Initialize self.  See help(type(self)) for accurate signature.


#### `from_dict(data: Dict[str, Any]) -> 'GameState'`

Deserialize GameState from dictionary (T123).


#### `to_dict(self) -> Dict[str, Any]`

Serialize GameState to dictionary (T123).

---

### `class InvalidImageError`

Raised when the provided image is invalid.

---

### `class Point`

A 2D point representing screen coordinates.

**Methods:**


#### `__init__(self, x: int, y: int) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class Rect`

A rectangle representing a bounding box.

**Methods:**


#### `__init__(self, x: int, y: int, width: int, height: int) -> None`

Initialize self.  See help(type(self)) for accurate signature.


#### `center(self) -> src.lib.types.Point`

Get the center point of the rectangle.


#### `contains(self, point: src.lib.types.Point) -> bool`

Check if a point is inside the rectangle.

---

### `class TextRegion`

Represents a region of text extracted from the game screen.

**Methods:**


#### `__init__(self, text: str, bounds: src.lib.types.Rect, confidence: float) -> None`

Initialize self.  See help(type(self)) for accurate signature.

---

### `class WindowNotFoundError`

Raised when the specified window cannot be found.

---
