"""
SQLite database initialization script for Cultist Simulator AI Agent.
Creates knowledge base schema from data-model.md.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "knowledge_base.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def create_database():
    """Initialize SQLite database with schema from data-model.md."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create agents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            agent_id TEXT PRIMARY KEY,
            created_at TIMESTAMP,
            strategy_version INTEGER,
            total_episodes INTEGER,
            knowledge_base_ref TEXT,
            model_checkpoint_path TEXT,
            config TEXT
        );
    """)

    # Create sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            agent_id TEXT REFERENCES agents(agent_id),
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            random_seed INTEGER,
            end_condition TEXT,
            win_type TEXT,
            survival_time_ingame REAL,
            resources_at_end TEXT,
            total_actions INTEGER,
            duration_seconds REAL,
            unique_mechanics_discovered INTEGER,
            loop_events INTEGER,
            safety_violations_blocked INTEGER
        );
    """)
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_sessions_agent ON sessions(agent_id);"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_sessions_end_condition ON sessions(end_condition);"
    )

    # Create actions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            action_id TEXT PRIMARY KEY,
            timestamp TIMESTAMP,
            episode_id TEXT REFERENCES sessions(session_id),
            pre_state_id TEXT,
            post_state_id TEXT,
            action_type TEXT,
            parameters TEXT,
            is_validated INTEGER,
            was_blocked INTEGER,
            execution_status TEXT,
            reward_signal REAL
        );
    """)
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_actions_episode ON actions(episode_id);"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_actions_type ON actions(action_type);"
    )

    # Create mechanics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mechanics (
            mechanic_id TEXT PRIMARY KEY,
            kb_id TEXT,
            description TEXT,
            evidence_count INTEGER,
            confidence REAL,
            conditions TEXT,
            effects TEXT,
            discovered_session TEXT REFERENCES sessions(session_id)
        );
    """)
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_mechanics_confidence ON mechanics(confidence);"
    )

    # Create strategies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategies (
            strategy_id TEXT PRIMARY KEY,
            name TEXT,
            version INTEGER,
            created_from_session TEXT REFERENCES sessions(session_id),
            goal_priorities TEXT,
            decision_rules TEXT,
            exploration_weight REAL,
            risk_tolerance REAL,
            sessions_played INTEGER,
            win_rate REAL,
            avg_survival_time REAL,
            parent_strategy_id TEXT REFERENCES strategies(strategy_id)
        );
    """)

    # Create metrics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            metric_id TEXT PRIMARY KEY,
            metric_type TEXT,
            agent_id TEXT REFERENCES agents(agent_id),
            timestamp TIMESTAMP,
            value REAL,
            unit TEXT,
            rolling_avg_10 REAL,
            rolling_avg_50 REAL,
            rolling_avg_100 REAL
        );
    """)
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_metrics_agent_type ON metrics(agent_id, metric_type);"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp);"
    )

    # Create safety_constraints table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS safety_constraints (
            constraint_id TEXT PRIMARY KEY,
            constraint_type TEXT,
            is_active INTEGER,
            priority INTEGER,
            validation_function TEXT,
            parameters TEXT,
            total_checks INTEGER,
            total_blocks INTEGER,
            last_violation TIMESTAMP
        );
    """)

    # Commit and close
    conn.commit()
    
    print(f"✓ Database initialized at: {DB_PATH}")
    print(f"✓ Created {cursor.execute('SELECT COUNT(*) FROM sqlite_master WHERE type=\"table\"').fetchone()[0]} tables")
    
    conn.close()


if __name__ == "__main__":
    create_database()
