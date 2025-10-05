#!/usr/bin/env python3
"""
API Documentation Generator - T131

Generates comprehensive API documentation from Python docstrings.
Creates markdown documentation for all public interfaces.
"""

import os
import sys
import inspect
import importlib
from pathlib import Path
from typing import Any, List, Dict
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class APIDocGenerator:
    """Generate API documentation from Python modules."""

    def __init__(self, output_dir: str = "docs/api"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.modules_to_document = [
            "src.vision",
            "src.automation",
            "src.safety",
            "src.nlp",
            "src.learning",
            "src.lib.types",
        ]

    def get_module_functions(self, module: Any) -> List[tuple]:
        """Get all public functions from a module."""
        functions = []
        for name, obj in inspect.getmembers(module):
            if inspect.isfunction(obj) and not name.startswith("_"):
                if hasattr(obj, "__module__") and obj.__module__.startswith("src"):
                    functions.append((name, obj))
        return functions

    def get_module_classes(self, module: Any) -> List[tuple]:
        """Get all public classes from a module."""
        classes = []
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and not name.startswith("_"):
                if hasattr(obj, "__module__") and obj.__module__.startswith("src"):
                    classes.append((name, obj))
        return classes

    def format_signature(self, func: Any) -> str:
        """Format function signature."""
        try:
            sig = inspect.signature(func)
            return str(sig)
        except (ValueError, TypeError):
            return "()"

    def format_docstring(self, obj: Any) -> str:
        """Format docstring with proper indentation."""
        doc = inspect.getdoc(obj)
        if not doc:
            return "*No documentation available*"
        return doc

    def generate_function_doc(self, name: str, func: Any) -> str:
        """Generate documentation for a function."""
        sig = self.format_signature(func)
        doc = self.format_docstring(func)

        return f"""
### `{name}{sig}`

{doc}

---
"""

    def generate_class_doc(self, name: str, cls: Any) -> str:
        """Generate documentation for a class."""
        doc = self.format_docstring(cls)

        # Get class methods
        methods = []
        for method_name, method in inspect.getmembers(cls):
            if inspect.isfunction(method) or inspect.ismethod(method):
                if not method_name.startswith("_") or method_name == "__init__":
                    methods.append((method_name, method))

        class_doc = f"""
### `class {name}`

{doc}

"""

        if methods:
            class_doc += "**Methods:**\n\n"
            for method_name, method in methods:
                sig = self.format_signature(method)
                method_doc = self.format_docstring(method)
                class_doc += f"""
#### `{method_name}{sig}`

{method_doc}

"""

        class_doc += "---\n"
        return class_doc

    def generate_module_doc(self, module_name: str) -> str:
        """Generate documentation for a module."""
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            print(f"Warning: Could not import {module_name}: {e}")
            return ""

        module_doc = inspect.getdoc(module) or f"API Documentation for {module_name}"

        # Build documentation
        doc = f"""# {module_name.replace('src.', '').replace('_', ' ').title()} API

{module_doc}

**Module**: `{module_name}`  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Table of Contents

- [Functions](#functions)
- [Classes](#classes)

---

"""

        # Get functions and classes
        functions = self.get_module_functions(module)
        classes = self.get_module_classes(module)

        # Functions section
        if functions:
            doc += "## Functions\n\n"
            for func_name, func in sorted(functions):
                doc += self.generate_function_doc(func_name, func)

        # Classes section
        if classes:
            doc += "\n## Classes\n\n"
            for class_name, cls in sorted(classes):
                doc += self.generate_class_doc(class_name, cls)

        return doc

    def generate_index(self, modules: List[str]) -> str:
        """Generate index page."""
        index = f"""# API Documentation Index

**Cultist Simulator AI Agent**  
**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This documentation covers all public APIs for the autonomous AI agent system.

---

## Libraries

"""

        for module in modules:
            module_title = module.replace("src.", "").replace("_", " ").title()
            module_file = module.replace("src.", "").replace(".", "_") + ".md"

            # Get module description
            try:
                mod = importlib.import_module(module)
                desc = inspect.getdoc(mod) or "No description available"
                first_line = desc.split("\n")[0]
            except:
                first_line = "API documentation"

            index += f"### [{module_title}]({module_file})\n\n{first_line}\n\n"

        index += """
---

## Quick Links

- [Vision Library](vision.md) - Screen capture, element detection, OCR
- [Automation Library](automation.md) - Safe input simulation
- [Safety Library](safety.md) - Constraint validation
- [NLP Library](nlp.md) - Narrative text analysis
- [Learning Library](learning.md) - RL agent and knowledge base
- [Type Definitions](lib_types.md) - Shared data structures

---

## Getting Started

Import libraries:

```python
from src.vision import capture_game_state, detect_elements
from src.automation import simulate_click, simulate_key_press
from src.safety import validate_action
from src.nlp import analyze_text, extract_goals
from src.learning import select_action, update_knowledge
```

## Example Usage

```python
# Capture game state
game_state = capture_game_state("Cultist Simulator")

# Select action
action = select_action(game_state)

# Validate with safety
validation = validate_action(action, context)

if validation.is_allowed:
    # Execute action
    result = simulate_click(action.point, "left", window_bounds)
```

---

## Architecture

The system consists of 5 main libraries:

1. **Vision** - Captures and analyzes game state
2. **Automation** - Executes actions safely
3. **Safety** - Validates all actions
4. **NLP** - Understands narrative text
5. **Learning** - Makes decisions and learns

All libraries use shared type definitions from `src.lib.types`.

---

## Testing

Run tests:
```bash
pytest tests/
```

All libraries have:
- Contract tests (interface validation)
- Unit tests (component testing)
- Integration tests (pipeline testing)
- Performance tests (NFR validation)

---

## Contributing

When adding new functions:
1. Add comprehensive docstrings
2. Include type hints
3. Write tests first (TDD)
4. Regenerate docs: `python3 scripts/generate_docs.py`

---

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
"""

        return index

    def generate_all(self):
        """Generate documentation for all modules."""
        print("=" * 60)
        print("API DOCUMENTATION GENERATOR")
        print("=" * 60)
        print(f"\nOutput directory: {self.output_dir}")
        print(f"Modules to document: {len(self.modules_to_document)}\n")

        generated = []

        for module_name in self.modules_to_document:
            print(f"Generating docs for {module_name}...")
            doc = self.generate_module_doc(module_name)

            if doc:
                # Create filename
                filename = module_name.replace("src.", "").replace(".", "_") + ".md"
                filepath = self.output_dir / filename

                # Write documentation
                with open(filepath, "w") as f:
                    f.write(doc)

                print(f"  ✅ Created {filepath}")
                generated.append(module_name)
            else:
                print(f"  ⚠️  Skipped {module_name} (no content)")

        # Generate index
        print("\nGenerating index...")
        index = self.generate_index(generated)
        index_path = self.output_dir / "index.md"

        with open(index_path, "w") as f:
            f.write(index)

        print(f"  ✅ Created {index_path}")

        print("\n" + "=" * 60)
        print("DOCUMENTATION GENERATION COMPLETE")
        print("=" * 60)
        print(f"\n📚 Generated {len(generated)} API documentation files")
        print(f"📁 Location: {self.output_dir}")
        print(f"📖 Start here: {index_path}")


def main():
    """Main entry point."""
    generator = APIDocGenerator()
    generator.generate_all()


if __name__ == "__main__":
    main()
