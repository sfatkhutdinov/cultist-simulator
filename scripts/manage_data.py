#!/usr/bin/env python3
"""
Data Management Utility

Provides tools to inspect, clean, and manage training data:
- View storage usage
- Clean old logs and TensorBoard runs
- Compact database
- Export data
"""

import argparse
import gzip
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List


def get_directory_size(path: Path) -> int:
    """Get total size of directory in bytes."""
    total = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                total += item.stat().st_size
    except Exception:
        pass
    return total


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size."""
    size = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def show_storage_info():
    """Display storage usage information."""
    print("\n" + "=" * 70)
    print("📊 STORAGE USAGE REPORT")
    print("=" * 70 + "\n")
    
    data_dir = Path("data")
    if not data_dir.exists():
        print("❌ data/ directory not found")
        return
    
    # Overall size
    total_size = get_directory_size(data_dir)
    print(f"Total data storage: {format_size(total_size)}\n")
    
    # Breakdown by subdirectory
    subdirs = [
        ("Logs", "logs"),
        ("TensorBoard", "tensorboard"),
        ("Checkpoints", "checkpoints"),
        ("Sessions", "sessions"),
        ("Database", "knowledge_base.db"),
    ]
    
    print("Breakdown:")
    print("-" * 70)
    
    for name, subpath in subdirs:
        path = data_dir / subpath
        if path.exists():
            if path.is_file():
                size = path.stat().st_size
                count = 1
            else:
                size = get_directory_size(path)
                count = len(list(path.rglob('*')))
            print(f"  {name:20s} {format_size(size):>10s}  ({count} items)")
        else:
            print(f"  {name:20s} {'0 B':>10s}  (empty)")
    
    print("-" * 70)
    
    # Log files detail
    logs_dir = data_dir / "logs"
    if logs_dir.exists():
        log_files = sorted(logs_dir.glob("agent_*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
        if log_files:
            print(f"\nRecent log files ({len(log_files)} total):")
            for log_file in log_files[:5]:
                size = format_size(log_file.stat().st_size)
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                print(f"  {log_file.name:40s} {size:>10s}  {mtime.strftime('%Y-%m-%d %H:%M')}")
            if len(log_files) > 5:
                print(f"  ... and {len(log_files) - 5} more")
    
    # TensorBoard runs detail
    tb_dir = data_dir / "tensorboard"
    if tb_dir.exists():
        tb_runs = sorted(tb_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        if tb_runs:
            print(f"\nTensorBoard runs ({len(tb_runs)} total):")
            for run in tb_runs[:5]:
                size = format_size(get_directory_size(run))
                mtime = datetime.fromtimestamp(run.stat().st_mtime)
                print(f"  {run.name:50s} {size:>10s}  {mtime.strftime('%Y-%m-%d %H:%M')}")
            if len(tb_runs) > 5:
                print(f"  ... and {len(tb_runs) - 5} more")
    
    # Database info
    db_path = data_dir / "knowledge_base.db"
    if db_path.exists():
        print(f"\nDatabase:")
        print(f"  Size: {format_size(db_path.stat().st_size)}")
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"  Tables: {len(tables)}")
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"    - {table[0]}: {count} rows")
            conn.close()
        except Exception as e:
            print(f"  Error reading database: {e}")
    
    print("\n" + "=" * 70 + "\n")


def cleanup_old_logs(days: int = 7, dry_run: bool = True):
    """Archive logs older than specified days."""
    print(f"\n{'DRY RUN: ' if dry_run else ''}Cleaning logs older than {days} days...")
    
    logs_dir = Path("data/logs")
    if not logs_dir.exists():
        print("No logs directory found")
        return
    
    archive_dir = logs_dir / "archive"
    cutoff_date = datetime.now() - timedelta(days=days)
    
    old_files = []
    for log_file in logs_dir.glob("agent_*.jsonl"):
        if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
            old_files.append(log_file)
    
    if not old_files:
        print("✓ No old logs to clean")
        return
    
    total_size = sum(f.stat().st_size for f in old_files)
    print(f"\nFound {len(old_files)} old log files ({format_size(total_size)}):")
    
    for log_file in old_files:
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        print(f"  {log_file.name} ({format_size(log_file.stat().st_size)}) - {mtime.strftime('%Y-%m-%d')}")
    
    if dry_run:
        print(f"\n💡 Run with --execute to actually archive these files")
        return
    
    # Create archive directory
    archive_dir.mkdir(exist_ok=True)
    
    # Move and compress
    for log_file in old_files:
        archive_path = archive_dir / log_file.name
        print(f"  Moving {log_file.name} to archive...")
        shutil.move(str(log_file), str(archive_path))
        
        print(f"  Compressing {log_file.name}...")
        with open(archive_path, 'rb') as f_in:
            with gzip.open(f"{archive_path}.gz", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        archive_path.unlink()  # Remove uncompressed
    
    print(f"\n✓ Archived {len(old_files)} files to {archive_dir}")


def cleanup_tensorboard(keep: int = 10, dry_run: bool = True):
    """Keep only the N most recent TensorBoard runs."""
    print(f"\n{'DRY RUN: ' if dry_run else ''}Cleaning TensorBoard (keeping {keep} most recent runs)...")
    
    tb_dir = Path("data/tensorboard")
    if not tb_dir.exists():
        print("No TensorBoard directory found")
        return
    
    runs = sorted(tb_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if len(runs) <= keep:
        print(f"✓ Only {len(runs)} runs exist, keeping all")
        return
    
    old_runs = runs[keep:]
    total_size = sum(get_directory_size(r) for r in old_runs)
    
    print(f"\nFound {len(old_runs)} old TensorBoard runs to remove ({format_size(total_size)}):")
    for run in old_runs:
        mtime = datetime.fromtimestamp(run.stat().st_mtime)
        size = get_directory_size(run)
        print(f"  {run.name} ({format_size(size)}) - {mtime.strftime('%Y-%m-%d')}")
    
    if dry_run:
        print(f"\n💡 Run with --execute to actually remove these directories")
        return
    
    for run in old_runs:
        print(f"  Removing {run.name}...")
        shutil.rmtree(run)
    
    print(f"\n✓ Removed {len(old_runs)} old TensorBoard runs")


def compact_database(dry_run: bool = True):
    """Compact the SQLite database."""
    print(f"\n{'DRY RUN: ' if dry_run else ''}Compacting database...")
    
    db_path = Path("data/knowledge_base.db")
    if not db_path.exists():
        print("Database not found")
        return
    
    old_size = db_path.stat().st_size
    print(f"Current size: {format_size(old_size)}")
    
    if dry_run:
        print("💡 Run with --execute to actually compact the database")
        return
    
    conn = sqlite3.connect(str(db_path))
    conn.execute("VACUUM")
    conn.close()
    
    new_size = db_path.stat().st_size
    saved = old_size - new_size
    print(f"New size: {format_size(new_size)}")
    print(f"✓ Saved {format_size(saved)}")


def main():
    parser = argparse.ArgumentParser(
        description="Manage training data storage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # View storage info
  python scripts/manage_data.py info
  
  # Preview log cleanup (7 days)
  python scripts/manage_data.py clean-logs --days 7
  
  # Actually clean logs older than 14 days
  python scripts/manage_data.py clean-logs --days 14 --execute
  
  # Keep only 5 most recent TensorBoard runs
  python scripts/manage_data.py clean-tensorboard --keep 5 --execute
  
  # Compact database
  python scripts/manage_data.py compact --execute
  
  # Clean everything
  python scripts/manage_data.py clean-all --execute
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Info command
    subparsers.add_parser("info", help="Show storage usage information")
    
    # Clean logs command
    logs_parser = subparsers.add_parser("clean-logs", help="Archive old log files")
    logs_parser.add_argument("--days", type=int, default=7, help="Archive logs older than N days")
    logs_parser.add_argument("--execute", action="store_true", help="Actually perform cleanup (default is dry-run)")
    
    # Clean TensorBoard command
    tb_parser = subparsers.add_parser("clean-tensorboard", help="Remove old TensorBoard runs")
    tb_parser.add_argument("--keep", type=int, default=10, help="Keep N most recent runs")
    tb_parser.add_argument("--execute", action="store_true", help="Actually perform cleanup (default is dry-run)")
    
    # Compact database command
    db_parser = subparsers.add_parser("compact", help="Compact database")
    db_parser.add_argument("--execute", action="store_true", help="Actually perform compaction (default is dry-run)")
    
    # Clean all command
    all_parser = subparsers.add_parser("clean-all", help="Run all cleanup tasks")
    all_parser.add_argument("--execute", action="store_true", help="Actually perform cleanup (default is dry-run)")
    
    args = parser.parse_args()
    
    if not args.command or args.command == "info":
        show_storage_info()
    
    elif args.command == "clean-logs":
        cleanup_old_logs(days=args.days, dry_run=not args.execute)
    
    elif args.command == "clean-tensorboard":
        cleanup_tensorboard(keep=args.keep, dry_run=not args.execute)
    
    elif args.command == "compact":
        compact_database(dry_run=not args.execute)
    
    elif args.command == "clean-all":
        cleanup_old_logs(days=7, dry_run=not args.execute)
        cleanup_tensorboard(keep=10, dry_run=not args.execute)
        compact_database(dry_run=not args.execute)
        if not args.execute:
            print("\n💡 Add --execute to actually perform all cleanup tasks")


if __name__ == "__main__":
    main()
