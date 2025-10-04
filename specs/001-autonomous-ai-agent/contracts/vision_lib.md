# Vision Library Contract

**Library**: `vision_lib`  
**Purpose**: Capture and interpret the current visual state of the Cultist Simulator game window on macOS  
**Dependencies**: OpenCV, YOLOv8, EasyOCR, Quartz (PyObjC)

---

## Public Interface

### Functions

#### `capture_game_state(window_name: str = "Cultist Simulator") -> GameState`
Captures the current visual state of the game window.

**Input**:
- `window_name`: Name of the game window to capture (default: "Cultist Simulator")

**Output**:
- `GameState` object containing:
  - Detected elements (cards, buttons, slots, timers)
  - Extracted numerical values (resources, health, time)
  - OCR'd narrative text
  - Window bounds and focus state

**Errors**:
- `WindowNotFoundError`: Game window not found
- `CaptureFailedError`: Screenshot capture failed
- `ProcessingTimeoutError`: Processing exceeded 500ms budget

**Performance**: Must complete in <500ms (NFR-001)

---

#### `detect_elements(screenshot: np.ndarray, element_types: List[ElementType]) -> List[GameElement]`
Identifies interactive UI elements in a screenshot.

**Input**:
- `screenshot`: RGB image array (H x W x 3)
- `element_types`: Which types to detect (e.g., [CARD, BUTTON, TIMER])

**Output**:
- List of `GameElement` objects with:
  - Type, bounding box, confidence
  - Visual signature for tracking
  - State indicators if available

**Errors**:
- `InvalidImageError`: Screenshot format invalid
- `ModelNotLoadedError`: YOLO model not initialized

**Performance**: <200ms for typical game screen

---

#### `extract_text_regions(screenshot: np.ndarray, regions: List[Rect]) -> List[NarrativeText]`
Performs OCR on specified regions of the screen.

**Input**:
- `screenshot`: RGB image array
- `regions`: Bounding boxes to perform OCR on (empty = auto-detect)

**Output**:
- List of `NarrativeText` objects with:
  - Extracted text string
  - Bounding box
  - Confidence score
  - Language detected

**Errors**:
- `OCRFailedError`: Text extraction failed
- `InvalidRegionError`: Region outside image bounds

**Performance**: <150ms for typical text regions

---

#### `track_element_changes(prev_state: GameState, curr_state: GameState) -> StateChanges`
Compares two game states to identify what changed.

**Input**:
- `prev_state`: Previous game state
- `curr_state`: Current game state

**Output**:
- `StateChanges` object with:
  - Added/removed elements
  - Moved elements (element, new position)
  - Resource value changes
  - New narrative text

**Errors**: None (returns empty changes if comparison fails)

**Performance**: <50ms

---

#### `get_window_bounds(window_name: str) -> Rect`
Gets the screen coordinates of the game window.

**Input**:
- `window_name`: Name of window to locate

**Output**:
- `Rect` with x, y, width, height in screen coordinates

**Errors**:
- `WindowNotFoundError`: Window not found

**Performance**: <10ms (used frequently for safety checks)

---

### CLI Interface

```bash
# Capture current game state and output as JSON
vision_lib --capture-game-state [--window "Cultist Simulator"] [--output state.json]

# Detect specific elements in a saved screenshot
vision_lib --detect-elements screenshot.png --types card,button,timer [--output elements.json]

# Extract text from image
vision_lib --extract-text screenshot.png [--regions "10,20,100,50;200,300,150,40"] [--output text.json]

# Get window bounds
vision_lib --window-bounds "Cultist Simulator" [--output bounds.json]

# Test vision pipeline performance
vision_lib --benchmark [--iterations 100]
```

**Output Format**: All commands output JSON to stdout unless --output specified. Errors go to stderr.

---

## Data Contracts

### GameState
```python
{
    "state_id": "uuid-string",
    "timestamp": "ISO-8601 datetime",
    "window_bounds": {"x": int, "y": int, "width": int, "height": int},
    "has_focus": bool,
    "detected_elements": [GameElement, ...],
    "resources": {"health": float, "funds": float, ...},
    "cards": [Card, ...],
    "timers": [Timer, ...],
    "narrative_text": [NarrativeText, ...],
    "screenshot_path": "optional-path-to-saved-image"
}
```

### GameElement
```python
{
    "element_id": "hash-string",
    "element_type": "card" | "button" | "slot" | "timer" | "text" | "icon" | "other",
    "bounding_box": {"x": int, "y": int, "width": int, "height": int},
    "confidence": float,  # 0.0-1.0
    "label": "optional-text",
    "state": "optional-state-indicator",
    "visual_signature": "base64-encoded-feature-vector-or-null"
}
```

### NarrativeText
```python
{
    "text": "extracted-string",
    "bounding_box": {"x": int, "y": int, "width": int, "height": int},
    "confidence": float,
    "language": "en" | "auto-detected"
}
```

---

## Error Handling

All errors inherit from `VisionLibError` base class.

```python
class VisionLibError(Exception):
    """Base error for vision library"""
    pass

class WindowNotFoundError(VisionLibError):
    """Game window not found on screen"""
    pass

class CaptureFailedError(VisionLibError):
    """Screenshot capture failed"""
    pass

class ProcessingTimeoutError(VisionLibError):
    """Processing exceeded time budget"""
    pass

class InvalidImageError(VisionLibError):
    """Image format invalid or corrupted"""
    pass

class ModelNotLoadedError(VisionLibError):
    """YOLO model not initialized"""
    pass

class OCRFailedError(VisionLibError):
    """Text extraction failed"""
    pass
```

---

## Configuration

```python
vision_config = {
    "window_name": "Cultist Simulator",
    "capture_resolution": (1920, 1080),  # Scale to this resolution
    "yolo_model_path": "models/game_elements.pt",
    "yolo_confidence_threshold": 0.5,
    "ocr_language": ["en"],
    "ocr_gpu": True,
    "template_cache_size": 100,
    "performance_budget_ms": 500
}
```

---

## Testing Requirements

### Contract Tests
1. `test_capture_returns_valid_gamestate()` - Verify output structure
2. `test_capture_within_time_budget()` - Performance requirement
3. `test_window_not_found_raises_error()` - Error handling
4. `test_detect_elements_finds_buttons()` - Detection accuracy (with mock screenshot)
5. `test_extract_text_handles_game_font()` - OCR capability
6. `test_cli_outputs_valid_json()` - CLI contract

### Integration Tests (with real game)
1. Capture game state during actual gameplay
2. Verify element detection accuracy (>80% precision/recall)
3. Verify OCR accuracy on narrative text (>90% word accuracy)
4. Test performance under continuous capture (60 captures/minute)

---

## Dependencies

```python
# requirements.txt for vision_lib
opencv-python>=4.8.0
ultralytics>=8.0.0  # YOLOv8
easyocr>=1.7.0
pyobjc-framework-Quartz>=9.0  # macOS window management
numpy>=1.24.0
Pillow>=10.0.0
```

---

## Initialization

```python
# Must be called before first use
vision_lib.initialize(config: dict) -> None

# Loads YOLO model, initializes OCR, sets up window management
# Raises: ModelLoadError if YOLO weights not found
```

---

## Thread Safety

- `capture_game_state()`: Thread-safe (uses locks internally)
- `detect_elements()`: Thread-safe (stateless)
- `extract_text_regions()`: Thread-safe (stateless)
- `track_element_changes()`: Thread-safe (pure function)
- `get_window_bounds()`: Thread-safe

**Note**: YOLO model inference may use GPU, shared across threads.

---

## Performance Benchmarks (Target)

| Operation | Target | Typical | Max Acceptable |
|-----------|--------|---------|----------------|
| Full capture_game_state() | <500ms | 250ms | 500ms |
| detect_elements() | <200ms | 120ms | 300ms |
| extract_text_regions() | <150ms | 80ms | 200ms |
| get_window_bounds() | <10ms | 2ms | 20ms |

---

## Example Usage

```python
from vision_lib import capture_game_state, get_window_bounds

# Initialize library
vision_lib.initialize(vision_config)

# Capture current state
try:
    state = capture_game_state()
    print(f"Found {len(state.detected_elements)} elements")
    print(f"Resources: {state.resources}")
    print(f"Window at: {state.window_bounds}")
except WindowNotFoundError:
    print("Game not running!")
```

```bash
# CLI usage
$ vision_lib --capture-game-state --output current_state.json
{
  "state_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-10-04T15:30:00Z",
  ...
}
```
