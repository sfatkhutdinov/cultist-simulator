"""
Configuration management for Cultist Simulator AI Agent.
T048: Configuration management (load YAML configs).

Loads configuration from YAML files with environment variable overrides.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dataclasses import dataclass, field


# Configuration directory
CONFIG_DIR = Path(__file__).parent.parent.parent / "config"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class VisionConfig:
    """Vision library configuration."""

    screenshot_interval_ms: int = 500
    yolo_confidence_threshold: float = 0.5
    ocr_confidence_threshold: float = 0.6
    max_capture_latency_ms: int = 500
    model_path: Optional[str] = None


@dataclass
class AutomationConfig:
    """Automation library configuration."""

    max_click_latency_ms: int = 50
    max_focus_check_latency_ms: int = 5
    default_drag_duration_ms: int = 200
    click_delay_ms: int = 10


@dataclass
class LearningConfig:
    """Learning library configuration."""

    max_action_selection_latency_ms: int = 500
    max_knowledge_query_latency_ms: int = 100
    max_loop_detection_latency_ms: int = 10
    learning_rate: float = 0.001
    exploration_rate: float = 0.1
    discount_factor: float = 0.99
    loop_detection_window_size: int = 20
    loop_detection_similarity_threshold: float = 0.8


@dataclass
class NLPConfig:
    """NLP library configuration."""

    max_analysis_latency_ms: int = 100
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384
    similarity_threshold: float = 0.7


@dataclass
class SafetyConfig:
    """Safety library configuration."""

    max_validation_latency_ms: int = 10
    rate_limit_actions_per_second: int = 10
    blacklisted_keys: list = field(
        default_factory=lambda: ["cmd+q", "cmd+w", "cmd+tab", "cmd+`", "escape", "f4"]
    )
    require_window_focus: bool = True
    enforce_bounds_checking: bool = True


@dataclass
class DatabaseConfig:
    """Database configuration."""

    db_path: str = "data/knowledge_base.db"
    connection_timeout: int = 30
    enable_wal: bool = True


@dataclass
class AgentConfig:
    """Complete agent configuration."""

    vision: VisionConfig = field(default_factory=VisionConfig)
    automation: AutomationConfig = field(default_factory=AutomationConfig)
    learning: LearningConfig = field(default_factory=LearningConfig)
    nlp: NLPConfig = field(default_factory=NLPConfig)
    safety: SafetyConfig = field(default_factory=SafetyConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    log_level: str = "INFO"
    window_name: str = "Cultist Simulator"


def load_config(config_file: Optional[str] = None) -> AgentConfig:
    """
    Load configuration from YAML file with environment variable overrides.

    Args:
        config_file: Path to YAML config file (default: config/agent.yaml)

    Returns:
        AgentConfig instance
    """
    # Default config
    config = AgentConfig()

    # Load from YAML if file exists
    if config_file is None:
        config_file = CONFIG_DIR / "agent.yaml"
    else:
        config_file = Path(config_file)

    if config_file.exists():
        with open(config_file, "r") as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config:
                config = _merge_config(config, yaml_config)

    # Override with environment variables
    config = _apply_env_overrides(config)

    return config


def save_config(config: AgentConfig, config_file: Optional[str] = None):
    """
    Save configuration to YAML file.

    Args:
        config: AgentConfig instance to save
        config_file: Path to YAML config file (default: config/agent.yaml)
    """
    if config_file is None:
        config_file = CONFIG_DIR / "agent.yaml"
    else:
        config_file = Path(config_file)

    # Convert dataclass to dict
    config_dict = _dataclass_to_dict(config)

    # Write to YAML
    with open(config_file, "w") as f:
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)


def _dataclass_to_dict(obj: Any) -> Dict[str, Any]:
    """Convert dataclass to dictionary recursively."""
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for field_name in obj.__dataclass_fields__:
            value = getattr(obj, field_name)
            result[field_name] = _dataclass_to_dict(value)
        return result
    elif isinstance(obj, list):
        return [_dataclass_to_dict(item) for item in obj]
    else:
        return obj


def _merge_config(base_config: AgentConfig, yaml_config: Dict[str, Any]) -> AgentConfig:
    """Merge YAML config into base config."""
    # Simple shallow merge for now
    # Could be enhanced for deep merge if needed
    for key, value in yaml_config.items():
        if hasattr(base_config, key):
            if isinstance(value, dict):
                # Merge nested config
                nested_config = getattr(base_config, key)
                for nested_key, nested_value in value.items():
                    if hasattr(nested_config, nested_key):
                        setattr(nested_config, nested_key, nested_value)
            else:
                setattr(base_config, key, value)
    return base_config


def _apply_env_overrides(config: AgentConfig) -> AgentConfig:
    """Apply environment variable overrides."""
    # Vision overrides
    if os.getenv("VISION_CONFIDENCE_THRESHOLD"):
        config.vision.yolo_confidence_threshold = float(
            os.getenv("VISION_CONFIDENCE_THRESHOLD")
        )

    # Learning overrides
    if os.getenv("LEARNING_RATE"):
        config.learning.learning_rate = float(os.getenv("LEARNING_RATE"))
    if os.getenv("EXPLORATION_RATE"):
        config.learning.exploration_rate = float(os.getenv("EXPLORATION_RATE"))

    # Safety overrides
    if os.getenv("REQUIRE_WINDOW_FOCUS"):
        config.safety.require_window_focus = (
            os.getenv("REQUIRE_WINDOW_FOCUS").lower() == "true"
        )

    # Database overrides
    if os.getenv("DB_PATH"):
        config.database.db_path = os.getenv("DB_PATH")

    # Logging overrides
    if os.getenv("LOG_LEVEL"):
        config.log_level = os.getenv("LOG_LEVEL")

    # Window name override
    if os.getenv("WINDOW_NAME"):
        config.window_name = os.getenv("WINDOW_NAME")

    return config


if __name__ == "__main__":
    # Test configuration management
    print("Testing configuration management...")

    # Load default config
    config = load_config()
    print(f"✓ Default config loaded")
    print(f"  Vision confidence: {config.vision.yolo_confidence_threshold}")
    print(f"  Learning rate: {config.learning.learning_rate}")
    print(f"  Safety max latency: {config.safety.max_validation_latency_ms}ms")
    print(f"  Window name: {config.window_name}")

    # Save config
    test_config_file = CONFIG_DIR / "test_agent.yaml"
    save_config(config, test_config_file)
    print(f"\n✓ Config saved to: {test_config_file}")

    # Load it back
    loaded_config = load_config(test_config_file)
    print(f"✓ Config loaded from file")
    print(f"  Learning rate: {loaded_config.learning.learning_rate}")

    # Test env override
    os.environ["LEARNING_RATE"] = "0.01"
    env_config = load_config()
    print(f"\n✓ Environment override applied")
    print(f"  Learning rate (from env): {env_config.learning.learning_rate}")

    print("\n✓ All configuration tests passed")
