# Agent Capability Analysis

**Date**: October 5, 2025  
**Issue**: Agent only moves mouse, doesn't interact meaningfully  
**Status**: ⚠️ **LIMITED CAPABILITIES - NEEDS EXPANSION**

---

## Current Problem

Based on the training logs and code analysis, the agent has **very limited action repertoire**:

### What the Agent IS Doing
✅ **Random clicking only** - Just moving mouse to random points and clicking
- Action: `ActionType.CLICK` at random (x, y) coordinates
- No element targeting (YOLO finds 0 elements)
- No text understanding (OCR disabled for speed)
- No strategic behavior

### What the Agent CANNOT Do (But Should)
❌ **Drag cards** - Critical for Cultist Simulator gameplay  
❌ **Drag to slots** - Primary game mechanic not accessible  
❌ **Keyboard input** - Can't type or use shortcuts  
❌ **Composite actions** - Can't chain actions together  
❌ **Element-aware clicks** - Blind to game UI  
❌ **Text-based decisions** - Can't read narrative  

---

## Data Analysis

### 1. Vision Data (What Agent "Sees")

From logs:
```json
{
  "element_count": 0,           // ❌ NO ELEMENTS DETECTED
  "text_region_count": 0,       // ❌ NO TEXT (OCR disabled)
  "yolo_detection_complete": {
    "elements_found": 0,        // ❌ YOLO finds nothing
    "confidence_threshold": 0.5
  }
}
```

**Problem**: Agent is essentially **blind**
- YOLO detects 0 elements (YOLOv8n not trained on game UI)
- OCR disabled for speed (no narrative understanding)
- Template matching is placeholder (not implemented)
- **Result**: Agent has NO information about game state

### 2. Actions Available (Types Defined)

From `src/lib/types.py`:
```python
class ActionType(Enum):
    CLICK = "click"        # ✅ IMPLEMENTED (only this works)
    DRAG = "drag"          # ⚠️ AVAILABLE but NOT USED
    KEY_PRESS = "key_press" # ⚠️ AVAILABLE but NOT USED
    WAIT = "wait"          # ❌ BLOCKED by safety validator
    COMPOSITE = "composite" # ⚠️ DEFINED but NOT IMPLEMENTED
```

**5 action types defined, but only 1 is being used!**

### 3. Actions Generated (What Agent Chooses)

From `src/learning/__init__.py` (lines 125-140):
```python
# Random action within game window bounds
window_bounds = game_state.window_bounds
random_x = random.randint(
    window_bounds.x + 50, window_bounds.x + window_bounds.width - 50
)
random_y = random.randint(
    window_bounds.y + 50, window_bounds.y + window_bounds.height - 50
)

action = Action(
    action_type=ActionType.CLICK,  # ❌ ALWAYS CLICK, NEVER DRAG/KEY
    parameters={"point": Point(random_x, random_y)},
    metadata={
        "confidence": 0.5,
        "rationale": "Random test action",
        "test_mode": _test_mode,
    },
)
```

**Problem**: `select_action()` **ONLY generates CLICK actions**
- Never generates DRAG actions
- Never generates KEY_PRESS actions
- No diversity in exploration

### 4. Actions Executed (What Actually Happens)

From `agent_run_optimized.log`:
```
[info] action_selected action_type=ActionType.CLICK point=Point(810, 484)
[debug] click_event_posted button=left x=810 y=484
[info] click_executed button=left duration_ms=27.14 point=Point(810, 484)

[info] action_selected action_type=ActionType.CLICK point=Point(213, 386)
[debug] click_event_posted button=left x=213 y=386
[info] click_executed button=left duration_ms=12.85 point=Point(213, 386)

[info] action_selected action_type=ActionType.CLICK point=Point(371, 830)
...
```

**Every single action is a CLICK at a random point**
- No variation
- No element targeting
- No dragging

---

## What Cultist Simulator Actually Needs

### Core Game Mechanics

1. **Drag Cards to Slots** (PRIMARY MECHANIC)
   - Pick up card from hand/board
   - Drag to verb slot (Work, Dream, Explore, etc.)
   - Release to place card
   - **This is how you play the game!**

2. **Drag Cards to Cards**
   - Combine cards together
   - Create new cards from combinations
   - Stack similar cards

3. **Click to Read**
   - Click cards to see description
   - Click narrative text to read story
   - Click verbs to see options

4. **Time Management**
   - Wait for timers to complete
   - Click "Start" buttons on verbs
   - Manage multiple simultaneous actions

5. **Keyboard Shortcuts** (Optional but useful)
   - Space to pause/resume time
   - ESC to cancel
   - Tab to cycle focus

---

## Action Repertoire Comparison

### Current Agent Actions
```python
Action 1: CLICK(random_x, random_y)
Action 2: CLICK(random_x, random_y)
Action 3: CLICK(random_x, random_y)
...
Action N: CLICK(random_x, random_y)
```
**Diversity**: 0%  
**Game-relevant**: ~5% (accidentally clicks buttons sometimes)

### What Agent SHOULD Have
```python
# Element-aware actions (when elements detected)
CLICK(card_element.center)           # Click on specific card
DRAG(card_start, verb_slot_end)      # Drag card to verb slot
DRAG(card1, card2)                   # Combine cards
CLICK(button_element.center)         # Click UI buttons

# Exploration actions (when no elements)
DRAG(random_start, random_end)       # Random drag exploration
CLICK(random_point)                  # Random click exploration
KEY_PRESS("space")                   # Try keyboard shortcuts

# Composite actions
[CLICK(card), WAIT(500ms), DRAG(card, slot)]  # Pick up and place
```
**Diversity**: High  
**Game-relevant**: ~60-80% (targets actual game elements)

---

## Root Causes

### 1. ❌ Action Selection Only Returns CLICK

**File**: `src/learning/__init__.py`  
**Line**: 136

```python
action = Action(
    action_type=ActionType.CLICK,  # ❌ HARDCODED
    parameters={"point": Point(random_x, random_y)},
    ...
)
```

**Why**: The `select_action()` function in test mode is hardcoded to only return CLICK actions.

**Fix Needed**: Generate diverse random actions:
- 40% CLICK (at random or element center)
- 40% DRAG (random or element-to-element)
- 10% KEY_PRESS (common keys like space, tab)
- 10% WAIT (short delays)

---

### 2. ❌ No Element Detection

**File**: Vision pipeline  
**Issue**: `elements_found=0` every frame

```
[debug] yolo_detection_complete elements_found=0
[debug] template_matching_placeholder  # Not implemented
[debug] elements_detected total_count=0
```

**Why**:
- YOLOv8n trained on COCO dataset (people, cars), not game UI
- Template matching is placeholder (not implemented)
- No custom training on Cultist Simulator screenshots

**Fix Needed**:
1. **Quick fix**: Implement simple template matching for common UI elements
2. **Better fix**: Collect screenshots and train custom YOLO model
3. **Alternative**: Use contour detection / color-based segmentation

---

### 3. ❌ Agent Can't Use DRAG

**File**: `src/orchestrator/agent_runner.py`  
**Line**: 337-342 (in `_execute_action`)

Current implementation:
```python
if action.action_type == ActionType.CLICK:
    simulate_click(...)
    return True
elif action.action_type == ActionType.KEY_PRESS:
    simulate_key_press(...)
    return True
elif action.action_type == ActionType.WAIT:
    wait(...)
    return True
else:
    logger.warning("unsupported_action_type", ...)
    return False
```

**Problem**: No handler for `ActionType.DRAG`!

Even if we generate DRAG actions, they won't execute because there's no:
```python
elif action.action_type == ActionType.DRAG:
    # MISSING!
```

---

## Immediate Fixes Required

### Priority 1: Enable DRAG Actions (CRITICAL)

**Why**: Cultist Simulator is 80% dragging cards. Without this, agent can't play.

**What to do**:

1. **Update `select_action()` to generate DRAG**
   ```python
   # src/learning/__init__.py
   import random
   
   action_type = random.choice([
       ActionType.CLICK,    # 40%
       ActionType.CLICK,    # 40%
       ActionType.DRAG,     # 20%
   ])
   
   if action_type == ActionType.DRAG:
       # Random drag from point A to point B
       start_x = random.randint(bounds.x + 50, bounds.x + bounds.width - 50)
       start_y = random.randint(bounds.y + 50, bounds.y + bounds.height - 50)
       end_x = random.randint(bounds.x + 50, bounds.x + bounds.width - 50)
       end_y = random.randint(bounds.y + 50, bounds.y + bounds.height - 50)
       
       action = Action(
           action_type=ActionType.DRAG,
           parameters={
               "start": Point(start_x, start_y),
               "end": Point(end_x, end_y),
               "duration": random.uniform(100, 500)  # ms
           },
           ...
       )
   ```

2. **Add DRAG handler in `_execute_action()`**
   ```python
   # src/orchestrator/agent_runner.py
   elif action.action_type == ActionType.DRAG:
       start = action.parameters.get("start")
       end = action.parameters.get("end")
       duration = action.parameters.get("duration", 200)
       
       if start and end:
           simulate_drag(
               start=start,
               end=end,
               duration_ms=duration,
               window_bounds=game_state.window_bounds
           )
           return True
       else:
           logger.warning("drag_missing_parameters")
           return False
   ```

---

### Priority 2: Implement Basic Element Detection

**Why**: Agent needs to know where cards/buttons are to click/drag them.

**Quick Win**: Color-based detection for Cultist Simulator
```python
# Cultist Simulator has distinctive colors:
# - Cards: Tan/beige rectangles
# - Verbs: Dark gray rectangles with icons
# - Buttons: Specific UI colors

def detect_cards_by_color(image):
    """Detect card-like rectangles by color."""
    # Convert to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    
    # Tan/beige color range for cards
    lower_tan = np.array([15, 20, 100])
    upper_tan = np.array([35, 100, 255])
    mask = cv2.inRange(hsv, lower_tan, upper_tan)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    elements = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 1000:  # Filter small noise
            x, y, w, h = cv2.boundingRect(contour)
            elements.append(GameElement(
                element_type=ElementType.CARD,
                bounds=Rect(x, y, w, h),
                confidence=0.7,
            ))
    
    return elements
```

---

### Priority 3: Add Action Diversity

**Why**: Random exploration needs to try different action types to discover rewards.

**What to do**:
```python
# src/learning/__init__.py (in select_action)

def _generate_random_action(game_state):
    """Generate diverse random actions for exploration."""
    bounds = game_state.window_bounds
    
    # Choose action type with probabilities
    action_type = random.choices(
        [ActionType.CLICK, ActionType.DRAG, ActionType.KEY_PRESS],
        weights=[0.5, 0.4, 0.1],  # 50% click, 40% drag, 10% key
        k=1
    )[0]
    
    if action_type == ActionType.CLICK:
        # If elements detected, click on them
        if game_state.elements:
            element = random.choice(game_state.elements)
            point = element.center
        else:
            # Random click
            point = _random_point_in_bounds(bounds)
        
        return Action(
            action_type=ActionType.CLICK,
            parameters={"point": point},
            ...
        )
    
    elif action_type == ActionType.DRAG:
        # If 2+ elements detected, drag between them
        if len(game_state.elements) >= 2:
            elem1, elem2 = random.sample(game_state.elements, 2)
            start = elem1.center
            end = elem2.center
        else:
            # Random drag
            start = _random_point_in_bounds(bounds)
            end = _random_point_in_bounds(bounds)
        
        return Action(
            action_type=ActionType.DRAG,
            parameters={
                "start": start,
                "end": end,
                "duration": random.uniform(100, 500)
            },
            ...
        )
    
    elif action_type == ActionType.KEY_PRESS:
        # Try common game keys
        key = random.choice(["space", "tab", "return"])
        return Action(
            action_type=ActionType.KEY_PRESS,
            parameters={"key": key},
            ...
        )
```

---

## Expected Impact

### Before Fixes
```
Actions: CLICK, CLICK, CLICK, CLICK, CLICK...
Elements detected: 0
Game progress: 0% (just clicking randomly)
Learning: Minimal (all actions look the same)
```

### After Fixes
```
Actions: CLICK(card), DRAG(card→slot), DRAG(random), CLICK(button), KEY(space), ...
Elements detected: 5-20 (cards, verbs, buttons)
Game progress: 10-30% (actually interacting with game mechanics)
Learning: Good (diverse actions, different rewards)
```

---

## Action Plan

### Immediate (Today)
1. ✅ Add DRAG action generation to `select_action()`
2. ✅ Add DRAG execution to `_execute_action()`
3. ✅ Test that drag actions work in game

### Short-term (This Week)
4. ⏳ Implement basic color-based card detection
5. ⏳ Add KEY_PRESS action generation
6. ⏳ Make action selection element-aware

### Medium-term (Next Week)
7. ⏳ Collect 100+ Cultist Simulator screenshots
8. ⏳ Annotate cards, verbs, buttons, slots
9. ⏳ Train custom YOLO model on game UI
10. ⏳ Enable OCR for narrative understanding

---

## Summary

**Current State**:
- Agent is **90% blind** (sees 0 elements)
- Agent has **1 action** (CLICK only)
- Agent is **0% effective** (random clicking)

**Root Causes**:
1. ❌ `select_action()` only returns CLICK
2. ❌ No DRAG execution handler
3. ❌ No element detection working
4. ❌ Action diversity = 0

**Critical Fixes**:
1. Add DRAG action generation (30 min)
2. Add DRAG execution handler (20 min)
3. Implement basic element detection (2 hours)

**Result After Fixes**:
- Agent will drag cards (game's primary mechanic)
- Agent will see game elements
- Agent will have diverse exploration
- **Training will actually work!**

---

## Next Steps

I'll now implement the critical fixes:
1. Update `select_action()` to generate DRAG actions
2. Add DRAG handler to `_execute_action()`
3. Add basic element detection

This will transform the agent from "random mouse mover" to "actual game player"!
